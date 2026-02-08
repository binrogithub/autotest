"""Deterministic report rendering for MCP runs."""

import json

REPORT_HEADER = "# Health Check Run Report"


def _format_block(data):
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False)


def render_report(run_record):
    """Render a deterministic markdown report for a run record."""
    sections = [REPORT_HEADER]
    sections.append("")
    sections.append("## Run Metadata")
    sections.append(f"- Run ID: `{run_record.get('run_id', '')}`")
    sections.append(f"- Created At: `{run_record.get('created_at', '')}`")
    sections.append("")
    sections.append("## Payload")
    sections.append("```")
    sections.append(_format_block(run_record.get("payload", {})))
    sections.append("```")
    sections.append("")
    sections.append("## Preview Result")
    sections.append("```")
    sections.append(_format_block(run_record.get("preview", {})))
    sections.append("```")
    sections.append("")
    sections.append("## Apply Result")
    sections.append("```")
    sections.append(_format_block(run_record.get("apply", {})))
    sections.append("```")
    return "\n".join(sections) + "\n"
