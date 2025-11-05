from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from .db import get_db
from .models import Agent, Artifact, Interaction, Space
from .schemas import AgentInteractionRequest
from .services.agent_interaction import execute_agent_interaction, summarize_space_state
from .nlp_utils import build_summary_and_tags
from .storage import remove_upload, save_upload

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/ui", tags=["ui"])


@router.get("/spaces")
def list_spaces(request: Request, db: Session = Depends(get_db)):
    spaces = db.query(Space).order_by(Space.created_at.desc()).all()
    return templates.TemplateResponse(
        request,
        "spaces_list.html",
        {"spaces": spaces},
    )


@router.post("/spaces")
def create_space(
    name: str = Form(...),
    description: str | None = Form(default=None),
    db: Session = Depends(get_db),
):
    space = Space(name=name, description=description)
    db.add(space)
    db.commit()
    db.refresh(space)
    return RedirectResponse(url=f"/ui/spaces/{space.id}", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/spaces/{space_id}")
def space_detail(
    space_id: int,
    request: Request,
    search: Optional[str] = Query(default=None, alias="q"),
    db: Session = Depends(get_db),
):
    space = (
        db.query(Space)
        .options(selectinload(Space.artifacts), selectinload(Space.agents))
        .filter(Space.id == space_id)
        .first()
    )
    if space is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Space not found")

    search_results: Optional[list[Artifact]] = None
    if search:
        pattern = f"%{search}%"
        search_results = (
            db.query(Artifact)
            .filter(
                Artifact.space_id == space_id,
                or_(
                    Artifact.title.ilike(pattern),
                    Artifact.content.ilike(pattern),
                    Artifact.file_name.ilike(pattern),
                ),
            )
            .order_by(Artifact.created_at.desc())
            .all()
        )

    interactions_by_agent: dict[int, list[Interaction]] = {}
    for agent in space.agents:
        interactions_by_agent[agent.id] = (
            db.query(Interaction)
            .filter(Interaction.agent_id == agent.id)
            .order_by(Interaction.created_at.desc())
            .all()
        )

    return templates.TemplateResponse(
        request,
        "space_detail.html",
        {
            "space": space,
            "search_query": search,
            "search_results": search_results,
            "interactions": interactions_by_agent,
        },
    )


@router.post("/spaces/{space_id}/artifacts")
async def create_artifact(
    space_id: int,
    title: str = Form(...),
    content: str | None = Form(default=None),
    file: Optional[UploadFile] = File(default=None),
    db: Session = Depends(get_db),
):
    space = db.query(Space).filter(Space.id == space_id).first()
    if space is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Space not found")

    stored_name = original_name = mime_type = None
    if file is not None and file.filename:
        stored_name, original_name, mime_type = await save_upload(file)

    artifact = Artifact(
        space_id=space_id,
        title=title,
        content=content,
        file_name=original_name,
        file_path=stored_name,
        mime_type=mime_type,
    )
    summary, tags = build_summary_and_tags(title, content or "")
    artifact.summary = summary or None
    artifact.tags = tags
    db.add(artifact)
    db.commit()
    return RedirectResponse(
        url=f"/ui/spaces/{space_id}", status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/spaces/{space_id}/artifacts/{artifact_id}/update")
def update_artifact(
    space_id: int,
    artifact_id: int,
    title: str = Form(...),
    content: str | None = Form(default=None),
    db: Session = Depends(get_db),
):
    artifact = (
        db.query(Artifact)
        .filter(Artifact.id == artifact_id, Artifact.space_id == space_id)
        .first()
    )
    if artifact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artifact not found")

    artifact.title = title
    artifact.content = content
    summary, tags = build_summary_and_tags(title, content or "")
    artifact.summary = summary or None
    artifact.tags = tags
    db.commit()
    return RedirectResponse(
        url=f"/ui/spaces/{space_id}", status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/spaces/{space_id}/artifacts/{artifact_id}/delete")
def delete_artifact(space_id: int, artifact_id: int, db: Session = Depends(get_db)):
    artifact = (
        db.query(Artifact)
        .filter(Artifact.id == artifact_id, Artifact.space_id == space_id)
        .first()
    )
    if artifact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artifact not found")

    remove_upload(artifact.file_path)
    db.delete(artifact)
    db.commit()
    return RedirectResponse(
        url=f"/ui/spaces/{space_id}", status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/spaces/{space_id}/agents")
def create_agent(
    space_id: int,
    name: str = Form(...),
    model: str = Form(...),
    provider: str = Form("echo"),
    description: str | None = Form(default=None),
    system_prompt: str | None = Form(default=None),
    db: Session = Depends(get_db),
):
    space = db.query(Space).filter(Space.id == space_id).first()
    if space is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Space not found")

    clean_system_prompt = system_prompt.strip() if system_prompt else None

    agent = Agent(
        space_id=space_id,
        name=name,
        model=model,
        provider=provider,
        description=description,
        system_prompt=clean_system_prompt,
    )
    db.add(agent)
    db.commit()
    return RedirectResponse(
        url=f"/ui/spaces/{space_id}", status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/spaces/{space_id}/agents/{agent_id}/update")
def update_agent_ui(
    space_id: int,
    agent_id: int,
    name: str = Form(...),
    model: str = Form(...),
    provider: str = Form(...),
    description: str | None = Form(default=None),
    system_prompt: str | None = Form(default=None),
    db: Session = Depends(get_db),
):
    agent = (
        db.query(Agent)
        .filter(Agent.id == agent_id, Agent.space_id == space_id)
        .first()
    )
    if agent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    clean_system_prompt = system_prompt.strip() if system_prompt else None

    agent.name = name
    agent.model = model
    agent.provider = provider
    agent.description = description
    agent.system_prompt = clean_system_prompt
    db.commit()
    return RedirectResponse(
        url=f"/ui/spaces/{space_id}", status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/spaces/{space_id}/agents/{agent_id}/summarize")
async def summarize_space_ui(
    space_id: int,
    agent_id: int,
    db: Session = Depends(get_db),
):
    agent = (
        db.query(Agent)
        .filter(Agent.id == agent_id, Agent.space_id == space_id)
        .first()
    )
    if agent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    summary = await summarize_space_state(agent, db)
    space = db.query(Space).filter(Space.id == space_id).first()
    if space is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Space not found")

    space.memory_summary = summary
    db.commit()

    return RedirectResponse(
        url=f"/ui/spaces/{space_id}?agent={agent_id}#agent-{agent_id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/spaces/{space_id}/agents/{agent_id}/delete")
def delete_agent_ui(space_id: int, agent_id: int, db: Session = Depends(get_db)):
    agent = (
        db.query(Agent)
        .filter(Agent.id == agent_id, Agent.space_id == space_id)
        .first()
    )
    if agent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    db.delete(agent)
    db.commit()
    return RedirectResponse(
        url=f"/ui/spaces/{space_id}", status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/spaces/{space_id}/agents/{agent_id}/chat")
async def chat_with_agent(
    request: Request,
    space_id: int,
    agent_id: int,
    prompt: str = Form(...),
    system: str | None = Form(default=None),
    context_limit: int = Form(default=5),
    db: Session = Depends(get_db),
):
    agent = (
        db.query(Agent)
        .filter(Agent.id == agent_id, Agent.space_id == space_id)
        .first()
    )
    if agent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    payload = AgentInteractionRequest(
        prompt=prompt,
        system=system,
        context_limit=context_limit,
    )

    try:
        output, metadata, artifacts_ctx, history_ctx, system_prompt_used = await execute_agent_interaction(
            agent, payload, db
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    interaction = Interaction(
        agent_id=agent.id,
        space_id=space_id,
        prompt=prompt,
        system_prompt=system_prompt_used,
        response=output,
        provider=agent.provider,
        model=agent.model,
    )
    interaction.context = {
        "artifacts": artifacts_ctx,
        "history": history_ctx,
        "system_prompt": system_prompt_used,
    }

    db.add(interaction)
    db.commit()

    # Check if this is an AJAX request
    if request.headers.get("accept") == "application/json" or "application/json" in request.headers.get("accept", ""):
        return {
            "output": output,
            "provider": agent.provider,
            "metadata": metadata,
            "context": {
                "artifacts": artifacts_ctx,
                "history": history_ctx,
                "system_prompt": system_prompt_used,
            }
        }

    return RedirectResponse(
        url=f"/ui/spaces/{space_id}?agent={agent_id}#agent-{agent_id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )
