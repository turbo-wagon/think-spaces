from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from .db import get_db
from .models import Agent, Artifact, Space
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

    return templates.TemplateResponse(
        request,
        "space_detail.html",
        {"space": space, "search_query": search, "search_results": search_results},
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
    description: str | None = Form(default=None),
    db: Session = Depends(get_db),
):
    space = db.query(Space).filter(Space.id == space_id).first()
    if space is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Space not found")

    agent = Agent(space_id=space_id, name=name, model=model, description=description)
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
    description: str | None = Form(default=None),
    db: Session = Depends(get_db),
):
    agent = (
        db.query(Agent)
        .filter(Agent.id == agent_id, Agent.space_id == space_id)
        .first()
    )
    if agent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    agent.name = name
    agent.model = model
    agent.description = description
    db.commit()
    return RedirectResponse(
        url=f"/ui/spaces/{space_id}", status_code=status.HTTP_303_SEE_OTHER
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
