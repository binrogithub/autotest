from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class RequestSpec:
    """Normalized request description for tool handlers."""

    action: str
    project_id: str
    resource_name: str
    params: Dict[str, Any]
