"""
Legacy command compatibility layer.

This module provides backward-compatible CLI commands
that map legacy workflows to the new execution model.
"""

import click


@click.group(name="legacy")
def legacy_group() -> None:
    """
    Legacy command namespace.
    """
    return None


@legacy_group.command(name="plan")
def legacy_plan() -> None:
    """
    Legacy plan command mapped to preview execution.
    """
    return None


@legacy_group.command(name="apply")
def legacy_apply() -> None:
    """
    Legacy apply command mapped to unified apply execution.
    """
    return None
