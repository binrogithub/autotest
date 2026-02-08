"""
CLI entry point for hc-agent.

This module defines the root command and wires together
all subcommands exposed by the hc-agent CLI.
"""

import click

from hc_agent.cli.cmd_doctor import doctor_group
from hc_agent.cli.cmd_legacy import legacy_group
from hc_agent.cli.cmd_run import run_group


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def main() -> None:
    """
    hc-agent command-line interface.

    Provides safe preview/apply execution for Huawei Cloud
    operations and demo orchestration.
    """
    return None


# Register subcommands
main.add_command(run_group)
main.add_command(doctor_group)
main.add_command(legacy_group)


if __name__ == "__main__":
    main()
