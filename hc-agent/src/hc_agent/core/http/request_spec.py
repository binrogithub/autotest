"""
Request specification model.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class RequestSpec:
    service: str
    region: str
    method: str
    endpoint: str
    path: str
    query: Optional[Dict[str, str]] = None
    headers: Optional[Dict[str, str]] = None
    json_body: Optional[Dict[str, Any]] = None
