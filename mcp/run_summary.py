"""Run summary and report generation utilities.

Example:
    report = generate_report({"run_id": "abc123"})
"""

from . import report_template


def generate_report(run_record):
    """Generate a report.md payload for a run record."""
    return report_template.render_report(run_record)


def write_report(path, run_record):
    """Write report.md content to disk."""
    report = generate_report(run_record)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(report)
    return report
