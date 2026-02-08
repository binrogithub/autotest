"""CLI entry point for the doctor selection logic."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping

from hc_agent import doctor


def _load_resources(path: Path | None) -> Iterable[Mapping[str, Any]]:
    if path is None:
        payload = sys.stdin.read().strip()
        if not payload:
            return []
        return json.loads(payload)
    return json.loads(path.read_text())


def _list_resources(path: Path | None) -> Iterable[Mapping[str, Any]]:
    return _load_resources(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run doctor selection using read-only listing data.",
    )
    parser.add_argument(
        "--resources-file",
        type=Path,
        help="Path to JSON list of resources (defaults to stdin).",
    )
    parser.add_argument(
        "--explicit",
        help="Explicit resource id or name to prioritize.",
    )
    parser.add_argument(
        "--default-tag",
        default="default",
        help="Tag name used to indicate default resources.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    result = doctor.run_doctor(
        lambda: _list_resources(args.resources_file),
        explicit_input=args.explicit,
        default_tag=args.default_tag,
    )

    output = {
        "ctx_patch": result.ctx_patch,
        "summary": result.summary,
    }
    json.dump(output, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

