from __future__ import annotations

from typing import List, Tuple

from sqlalchemy.orm import Session

from ..llm import CompletionRequest, registry
from ..models import Agent, Artifact, Interaction
from ..schemas import AgentInteractionRequest


async def execute_agent_interaction(
    agent: Agent, payload: AgentInteractionRequest, db: Session
) -> Tuple[str, dict, List[dict]]:
    default_system_prompt = (
        "You are a Think Spaces companion. Always weave in the most relevant "
        "artifacts from the current space (use their titles, summaries, or tags "
        "as supporting evidence), surface follow-up questions that move the idea "
        "forward, and keep responses concise, positive, and actionable. Prefer "
        "concrete suggestions over abstractions, and explicitly call out when the "
        "artifact context is insufficient."
    )

    provider_cls = registry.get(agent.provider)
    if provider_cls is None:
        raise RuntimeError(f"Provider '{agent.provider}' is not available")

    try:
        provider = provider_cls(model=agent.model)
    except TypeError:
        provider = provider_cls()
    except RuntimeError as exc:
        raise RuntimeError(str(exc)) from exc

    context_items = _build_context(agent, payload.context_limit, db)
    context_strings = [
        formatted
        for item in context_items
        if (formatted := _format_context_item(item))
    ]

    history_items = _build_history(agent, db)
    history_strings = [_format_history_item(item) for item in history_items]

    system_prompt = (
        payload.system
        if payload.system is not None
        else agent.system_prompt or default_system_prompt
    )

    request = CompletionRequest(
        prompt=payload.prompt,
        system=system_prompt,
        context=[*history_strings, *context_strings],
        options={"model": agent.model},
    )

    completion = await provider.generate(request)
    return completion.output, dict(completion.metadata), [
        {**item, "type": "artifact"} for item in context_items
    ] + [
        {
            "type": "history",
            "prompt": item.prompt,
            "response": item.response,
            "created_at": item.created_at.isoformat(),
        }
        for item in history_items
    ]


def _build_context(agent: Agent, limit: int, db: Session) -> List[dict]:
    if not limit:
        return []

    artifacts = (
        db.query(Artifact)
        .filter(Artifact.space_id == agent.space_id)
        .order_by(Artifact.created_at.desc())
        .limit(limit)
        .all()
    )

    context = []
    for artifact in artifacts:
        context.append(
            {
                "title": artifact.title,
                "summary": artifact.summary
                or (artifact.content[:160] + "…" if artifact.content else ""),
                "tags": artifact.tags,
                "artifact_id": artifact.id,
            }
        )
    return context


def _format_context_item(item: dict) -> str:
    parts = []
    if item.get("title"):
        parts.append(f"Title: {item['title']}")
    if item.get("summary"):
        parts.append(f"Summary: {item['summary']}")
    if item.get("tags"):
        parts.append("Tags: " + ", ".join(item["tags"]))
    return "\n".join(parts)


def _build_history(agent: Agent, db: Session, limit: int = 3) -> List[Interaction]:
    return (
        db.query(Interaction)
        .filter(Interaction.agent_id == agent.id)
        .order_by(Interaction.created_at.desc())
        .limit(limit)
        .all()
    )


def _format_history_item(interaction: Interaction) -> str:
    parts = [
        f"Previous prompt: {interaction.prompt}",
        f"Previous response: {interaction.response}",
    ]
    return "\n".join(parts)
