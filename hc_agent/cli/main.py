"""hc-agent command line interface."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List, Optional


def _add_global_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config", help="Path to configuration file.")
    parser.add_argument("--region", help="Target region.")
    parser.add_argument("--mode", help="Execution mode.")
    parser.add_argument("--run-id", help="Run identifier.")
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Disable interactive prompts.",
    )
    parser.add_argument("--tenant", help="Tenant identifier.")
    parser.add_argument("--policy", help="Policy identifier.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable output.",
    )


def _global_options(args: argparse.Namespace) -> Dict[str, Any]:
    return {
        "config": args.config,
        "region": args.region,
        "mode": args.mode,
        "run_id": args.run_id,
        "non_interactive": args.non_interactive,
        "tenant": args.tenant,
        "policy": args.policy,
    }


def _emit(action: str, args: argparse.Namespace, extra: Optional[Dict[str, Any]] = None) -> int:
    payload = {
        "action": action,
        "options": _global_options(args),
        "extra": extra or {},
    }
    if args.json:
        print(json.dumps(payload, sort_keys=True))
    else:
        print(f"action={action}")
        for key, value in payload["options"].items():
            if value is not None and value is not False:
                print(f"{key}={value}")
        for key, value in payload["extra"].items():
            print(f"{key}={value}")
    return 0


def _handle_run_single(args: argparse.Namespace) -> int:
    return _emit("run.single", args)


def _handle_run_demo(args: argparse.Namespace) -> int:
    return _emit("run.demo", args)


def _handle_doctor_fix(args: argparse.Namespace) -> int:
    return _emit("doctor.fix", args)


def _handle_legacy_passthrough(args: argparse.Namespace) -> int:
    extra = {"args": args.legacy_args}
    return _emit(f"legacy.{args.legacy_command}", args, extra=extra)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hc-agent")
    _add_global_flags(parser)

    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run commands.")
    run_subparsers = run_parser.add_subparsers(dest="run_command", required=True)
    run_single = run_subparsers.add_parser("single", help="Run a single execution.")
    run_single.set_defaults(func=_handle_run_single)
    run_demo = run_subparsers.add_parser("demo", help="Run a demo execution.")
    run_demo.set_defaults(func=_handle_run_demo)

    doctor_parser = subparsers.add_parser("doctor", help="Doctor commands.")
    doctor_subparsers = doctor_parser.add_subparsers(dest="doctor_command", required=True)
    doctor_fix = doctor_subparsers.add_parser("fix", help="Attempt to fix issues.")
    doctor_fix.set_defaults(func=_handle_doctor_fix)

    legacy_parser = subparsers.add_parser("legacy", help="Legacy passthrough.")
    legacy_subparsers = legacy_parser.add_subparsers(dest="legacy_command", required=True)
    legacy_plan = legacy_subparsers.add_parser("plan", help="Legacy plan passthrough.")
    legacy_plan.add_argument("legacy_args", nargs=argparse.REMAINDER)
    legacy_plan.set_defaults(func=_handle_legacy_passthrough)
    legacy_apply = legacy_subparsers.add_parser("apply", help="Legacy apply passthrough.")
    legacy_apply.add_argument("legacy_args", nargs=argparse.REMAINDER)
    legacy_apply.set_defaults(func=_handle_legacy_passthrough)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = getattr(args, "func", None)
    if handler is None:
        parser.error("No command specified.")
    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
