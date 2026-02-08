"""
Run commands for hc-agent.

This module provides CLI commands that map to the unified
execution gateway, including single-tool runs and demo runs.
"""

import click


@click.group(name="run")
def run_group() -> None:
    """
    Execute cloud operations using preview or apply mode.
    """
    return None


@run_group.command(name="single")
@click.option("--mode", type=click.Choice(["preview", "apply"]), required=True)
@click.option("--tool", required=True, help="Registry tool name")
@click.option("--region", required=True)
@click.option("--config", "config_path", required=True)
@click.option("--run-id", required=False)
@click.option("--approve-token", required=False)
@click.option("--safety-ack", required=False)
def run_single(
    mode: str,
    tool: str,
    region: str,
    config_path: str,
    run_id: str | None,
    approve_token: str | None,
    safety_ack: str | None,
) -> None:
    """
    Run a single tool through the unified runner.
    """
    _ = (mode, tool, region, config_path, run_id, approve_token, safety_ack)
    return None


@run_group.command(name="demo")
@click.option("--mode", type=click.Choice(["preview", "apply"]), required=True)
@click.option("--region", required=True)
@click.option("--config", "config_path", required=True)
@click.option("--run-id", required=False)
@click.option("--approve-token", required=False)
@click.option("--safety-ack", required=False)
def run_demo(
    mode: str,
    region: str,
    config_path: str,
    run_id: str | None,
    approve_token: str | None,
    safety_ack: str | None,
) -> None:
    """
    Run the built-in demo orchestration.
    """
    _ = (mode, region, config_path, run_id, approve_token, safety_ack)
    return None
