"""Selection logic for choosing the best agent candidate."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable, Mapping, Optional

DEFAULT_TAG_KEY = "hc-agent-default"


def select_agent(
    agents: Iterable[Mapping[str, Any]],
    explicit: Optional[Any] = None,
    config: Optional[Any] = None,
) -> Optional[Mapping[str, Any]]:
    """Select an agent based on explicit/config/default tag ordering.

    Order:
      1. Explicit argument or config value (if present and matches).
      2. Candidates tagged with hc-agent-default=true.
      3. Tie-break by ACTIVE + newest created_at, else lexical.
    """
    agents_list = list(agents)
    if not agents_list:
        return None

    preferred = explicit if explicit is not None else config
    if preferred is not None:
        matched = _match_agent(agents_list, preferred)
        if matched is not None:
            return matched

    tagged = [agent for agent in agents_list if _has_default_tag(agent)]
    candidates = tagged or agents_list
    return _pick_best(candidates)


def _match_agent(agents: Iterable[Mapping[str, Any]], preferred: Any) -> Optional[Mapping[str, Any]]:
    if isinstance(preferred, Mapping):
        preferred_id = preferred.get("id") or preferred.get("name")
        if preferred_id is None:
            return None
    else:
        preferred_id = str(preferred)

    for agent in agents:
        if str(agent.get("id")) == preferred_id:
            return agent
        if str(agent.get("name")) == preferred_id:
            return agent
    return None


def _has_default_tag(agent: Mapping[str, Any]) -> bool:
    tags = agent.get("tags") or {}
    if isinstance(tags, Mapping):
        value = tags.get(DEFAULT_TAG_KEY)
        return _truthy(value)
    if isinstance(tags, (list, tuple, set)):
        for tag in tags:
            if isinstance(tag, Mapping):
                if tag.get("key") == DEFAULT_TAG_KEY and _truthy(tag.get("value")):
                    return True
            elif isinstance(tag, str):
                if tag.lower() == f"{DEFAULT_TAG_KEY}=true":
                    return True
    return False


def _truthy(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() == "true"
    return bool(value)


def _pick_best(candidates: Iterable[Mapping[str, Any]]) -> Optional[Mapping[str, Any]]:
    candidates_list = list(candidates)
    if not candidates_list:
        return None

    active_candidates = [agent for agent in candidates_list if _is_active(agent)]
    if active_candidates:
        return max(active_candidates, key=_active_sort_key)

    return min(candidates_list, key=_lexical_key)


def _is_active(agent: Mapping[str, Any]) -> bool:
    status = agent.get("status") or agent.get("state") or ""
    return str(status).upper() == "ACTIVE"


def _active_sort_key(agent: Mapping[str, Any]) -> tuple:
    return (_created_at_timestamp(agent), _lexical_key(agent))


def _created_at_timestamp(agent: Mapping[str, Any]) -> float:
    created_at = agent.get("created_at")
    if created_at is None:
        return 0.0
    if isinstance(created_at, (int, float)):
        return float(created_at)
    if isinstance(created_at, datetime):
        return created_at.timestamp()
    if isinstance(created_at, str):
        try:
            normalized = created_at.replace("Z", "+00:00")
            return datetime.fromisoformat(normalized).timestamp()
        except ValueError:
            return 0.0
    return 0.0


def _lexical_key(agent: Mapping[str, Any]) -> str:
    return str(agent.get("name") or agent.get("id") or "")
