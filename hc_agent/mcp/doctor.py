"""Resolve missing MCP parameters using deterministic rules.

Rules order:
1) Explicit values already in ctx win.
2) Tagged defaults (e.g. "default", "recommended") are preferred.
3) Stable tie-break among remaining candidates.

This module only performs read-only listing calls provided by callers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Set

DEFAULT_TAGS: Set[str] = {"default", "recommended"}


@dataclass(frozen=True)
class Candidate:
    """A possible value for a missing parameter."""

    value: Any
    tags: Set[str]
    raw: Any


@dataclass(frozen=True)
class Resolution:
    """Resolution result with a context patch and human-readable explanations."""

    ctx_patch: Dict[str, Any]
    explanations: List[str]


def _coerce_candidate(item: Any) -> Candidate:
    if isinstance(item, Candidate):
        return item
    if isinstance(item, Mapping):
        value = item.get("value")
        if value is None:
            for key in ("name", "id", "key"):
                if key in item:
                    value = item[key]
                    break
        tags = set(item.get("tags", []) or [])
        return Candidate(value=value, tags=tags, raw=item)
    return Candidate(value=item, tags=set(), raw=item)


def _stable_key(candidate: Candidate) -> str:
    return f"{repr(candidate.value)}|{sorted(candidate.tags)}"


def resolve_missing_parameters(
    ctx: Mapping[str, Any],
    missing: Iterable[str],
    list_calls: Mapping[str, Callable[[], Sequence[Any]]],
    *,
    default_tags: Optional[Set[str]] = None,
) -> Resolution:
    """Resolve missing parameters and return a ctx_patch with explanations.

    Args:
        ctx: Current context containing explicit values.
        missing: Names of parameters that need resolution.
        list_calls: Mapping of parameter -> callable that returns candidate values.
            These callables must only perform read-only listing operations.
        default_tags: Optional override for which tags represent defaults.
    """

    tags = default_tags or DEFAULT_TAGS
    ctx_patch: Dict[str, Any] = {}
    explanations: List[str] = []

    for param in missing:
        if param in ctx and ctx[param] is not None:
            explanations.append(
                f"{param}: explicit value '{ctx[param]}' retained; no resolution needed."
            )
            continue

        list_call = list_calls.get(param)
        if list_call is None:
            explanations.append(f"{param}: no listing call available; left unresolved.")
            continue

        candidates_raw = list_call() or []
        candidates = [_coerce_candidate(item) for item in candidates_raw]
        if not candidates:
            explanations.append(f"{param}: listing returned no candidates; left unresolved.")
            continue

        tagged = [c for c in candidates if c.tags.intersection(tags)]
        pool = tagged if tagged else candidates
        chosen = sorted(pool, key=_stable_key)[0]
        ctx_patch[param] = chosen.value
        if tagged:
            explanations.append(
                f"{param}: selected tagged default '{chosen.value}' from {len(tagged)} candidates."
            )
        else:
            explanations.append(
                f"{param}: selected '{chosen.value}' via stable tie-break from {len(candidates)} candidates."
            )

    return Resolution(ctx_patch=ctx_patch, explanations=explanations)


def apply_ctx_patch(ctx: MutableMapping[str, Any], patch: Mapping[str, Any]) -> None:
    """Apply a ctx patch in-place."""

    ctx.update(patch)
