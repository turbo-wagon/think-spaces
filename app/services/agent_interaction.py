from __future__ import annotations

from typing import List, Tuple

from sqlalchemy.orm import Session

from ..llm import CompletionRequest, registry
from ..models import Agent, Artifact
from ..schemas import AgentInteractionRequest


async def execute_agent_interaction(
    agent: Agent, payload: AgentInteractionRequest, db: Session
) -> Tuple[str, dict, List[dict]]:
    provider_cls = registry.get(agent.provider)
    if provider_cls is None:
        raise RuntimeError(f\"Provider '{agent.provider}' is not available\")

    try:
        provider = provider_cls(model=agent.model)
    except TypeError:
        provider = provider_cls()
    except RuntimeError as exc:
        raise RuntimeError(str(exc)) from exc

    context_items = _build_context(agent, payload.context_limit, db)
    context_strings = [
        _format_context_item(item) for item in context_items if _format_context_item(item)
    ]

    request = CompletionRequest(
        prompt=payload.prompt,
        system=payload.system,
        context=context_strings,
        options={\"model\": agent.model},
    )

    completion = await provider.generate(request)
    return completion.output, dict(completion.metadata), context_items


def _build_context(
    agent: Agent, limit: int, db: Session
) -> List[dict]:
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
                \"title\": artifact.title,
                \"summary\": artifact.summary or (artifact.content[:160] + \"…\" if artifact.content else \"\"),
                \"tags\": artifact.tags,
                \"artifact_id\": artifact.id,
            }
        )
    return context


def _format_context_item(item: dict) -> str:
    parts = [f\"Title: {item['title']}\"] if item.get(\"title\") else []
    if item.get(\"summary\"):\n+        parts.append(f\"Summary: {item['summary']}\")\n+    if item.get(\"tags\"):\n+        parts.append(\"Tags: \" + \", \".join(item[\"tags\"]))\n+    return \"\\n\".join(parts)\n*** End Patch
