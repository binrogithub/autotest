"""Doctor module for deterministic resource selection with read-only listings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping, Sequence


@dataclass(frozen=True)
class DoctorResult:
    """Outcome from a doctor selection run."""

    ctx_patch: dict[str, Any]
    summary: str


def _normalize_tags(tags: Any) -> dict[str, Any]:
    if tags is None:
        return {}
    if isinstance(tags, Mapping):
        return dict(tags)
    if isinstance(tags, Sequence) and not isinstance(tags, (str, bytes)):
        return {str(tag): True for tag in tags}
    return {str(tags): True}


def _is_tagged_default(tags: Any, default_tag: str) -> bool:
    normalized = _normalize_tags(tags)
    if default_tag in normalized:
        value = normalized[default_tag]
        if isinstance(value, str):
            return value.strip().lower() in {"true", "yes", "1", "default"}
        return bool(value)
    return False


def _stable_sort_key(resource: Mapping[str, Any]) -> tuple[str, str]:
    name = str(resource.get("name", ""))
    resource_id = str(resource.get("id", ""))
    return (name, resource_id)


def _select_candidate(resources: Iterable[Mapping[str, Any]]) -> Mapping[str, Any] | None:
    sorted_resources = sorted(resources, key=_stable_sort_key)
    return sorted_resources[0] if sorted_resources else None


def run_doctor(
    list_resources: Callable[[], Iterable[Mapping[str, Any]]],
    *,
    explicit_input: str | None = None,
    default_tag: str = "default",
) -> DoctorResult:
    """Run doctor selection using read-only list_resources calls.

    Selection precedence:
      1. explicit_input (id or name match)
      2. resources tagged with default_tag
      3. stable tie-breaker (name, id)
    """

    resources = list(list_resources())
    summary_parts = [f"resources={len(resources)}"]
    selected: Mapping[str, Any] | None = None
    reason = ""

    if explicit_input:
        matches = [
            resource
            for resource in resources
            if str(resource.get("id")) == explicit_input
            or str(resource.get("name")) == explicit_input
        ]
        selected = _select_candidate(matches)
        if selected:
            reason = "explicit"
        else:
            summary_parts.append("explicit_input_not_found=true")

    if selected is None:
        tagged = [
            resource
            for resource in resources
            if _is_tagged_default(resource.get("tags"), default_tag)
        ]
        selected = _select_candidate(tagged)
        if selected:
            reason = "tagged_default"

    if selected is None:
        selected = _select_candidate(resources)
        if selected:
            reason = "stable_tiebreak"

    ctx_patch = {
        "doctor": {
            "selected": {
                "id": None if selected is None else selected.get("id"),
                "name": None if selected is None else selected.get("name"),
                "reason": reason or None,
            },
            "default_tag": default_tag,
        }
    }

    if selected is None:
        summary_parts.append("selected=none")
    else:
        summary_parts.append(
            f"selected={selected.get('name', selected.get('id', 'unknown'))}"
        )
        summary_parts.append(f"reason={reason}")

    summary = "; ".join(summary_parts)
    return DoctorResult(ctx_patch=ctx_patch, summary=summary)

