from __future__ import annotations

from typing import List, Tuple

from sqlalchemy.orm import Session

from ..llm import CompletionRequest, registry
from ..models import Agent, Artifact, Interaction, Space
from ..schemas import AgentInteractionRequest


async def execute_agent_interaction(
    agent: Agent, payload: AgentInteractionRequest, db: Session
) -> Tuple[str, dict, List[dict], List[dict], str]:
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

    context_artifacts = _build_context(agent, payload.context_limit, db)
    context_strings = [
        formatted
        for item in context_artifacts
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
    history_payload = [
        {
            "prompt": item.prompt,
            "response": item.response,
            "created_at": item.created_at.isoformat(),
        }
        for item in history_items
    ]
    return completion.output, dict(completion.metadata), context_artifacts, history_payload, system_prompt


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
        parts.append(f"Artifact: {item['title']}")
    if item.get("summary"):
        parts.append(f"Summary: {item['summary']}")
    if item.get("tags"):
        parts.append("Tags: " + ", ".join(item["tags"]))
    return "\n".join(parts)


def _build_history(agent: Agent, db: Session, limit: int = 10) -> List[Interaction]:
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


async def summarize_space_state(agent: Agent, db: Session) -> str:
    provider_cls = registry.get(agent.provider)
    if provider_cls is None:
        raise RuntimeError(f"Provider '{agent.provider}' is not available")

    try:
        provider = provider_cls(model=agent.model)
    except TypeError:
        provider = provider_cls()
    except RuntimeError as exc:
        raise RuntimeError(str(exc)) from exc

    artifacts = (
        db.query(Artifact)
        .filter(Artifact.space_id == agent.space_id)
        .order_by(Artifact.created_at.desc())
        .all()
    )

    lines = []
    for artifact in artifacts:
        line = f"- {artifact.title}"
        if artifact.summary:
            line += f": {artifact.summary}"
        lines.append(line)

    interactions = (
        db.query(Interaction)
        .filter(Interaction.space_id == agent.space_id)
        .order_by(Interaction.created_at.desc())
        .limit(5)
        .all()
    )

    history_lines = [
        f"Prompt: {interaction.prompt}\nResponse: {interaction.response}"
        for interaction in interactions
    ]

    summary_prompt = (
        "You are the space memory steward for a Think Space. Produce a concise "
        "narrative summary that captures: 1) the core themes across the current "
        "artifacts (mention titles and key points), 2) the latest conversation "
        "highlights (major decisions, questions, or ideas), and 3) suggested next "
        "steps or open questions to explore. Use a calm, encouraging tone. Keep "
        "it under 6 sentences. If information is thin, clearly state what’s missing "
        "instead of guessing."
    )

    prompt = (
        "Artifacts collected in this space:\n"
        + ("\n".join(lines) if lines else "(none yet)")
        + "\n\nRecent conversation exchanges:\n"
        + ("\n\n".join(history_lines) if history_lines else "(no recent exchanges)")
    )

    request = CompletionRequest(
        prompt=prompt,
        system=summary_prompt,
        context=[],
        options={"model": agent.model},
    )

    completion = await provider.generate(request)
    return completion.output
