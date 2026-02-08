"""Gateway handlers for evidence persistence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

from hc_agent.core.evidence import build_min_evidence


def write_evidence_json(evidence: Mapping[str, object], output_dir: str | Path) -> Path:
    """Write minimal evidence payload to evidence.json and return its path."""
    output_path = Path(output_dir) / "evidence.json"
    minimal_evidence = build_min_evidence(evidence)

    output_path.write_text(
        json.dumps(minimal_evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output_path
