import re
import unittest
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

try:
    from importlib import metadata
except ImportError:  # pragma: no cover - python <3.8 fallback
    import importlib_metadata as metadata


def _load_console_script(name: str):
    entry_points = metadata.entry_points()
    if hasattr(entry_points, "select"):
        matches = entry_points.select(group="console_scripts", name=name)
    else:
        matches = [
            entry_point
            for entry_point in entry_points.get("console_scripts", [])
            if entry_point.name == name
        ]
    if not matches:
        raise AssertionError(f"Console script '{name}' was not found in entry points.")
    return matches[0].load()


def _extract_run_id(output: str):
    match = re.search(r"run[_-]?id\s*[:=]?\s*([A-Za-z0-9_-]+)", output, re.IGNORECASE)
    return match.group(1) if match else None


class TestCliSmoke(unittest.TestCase):
    def test_hc_agent_run_demo_preview(self):
        runner = CliRunner()
        command = _load_console_script("hc-agent")
        with runner.isolated_filesystem():
            config_path = Path("config.json")
            config_path.write_text("{}\n", encoding="utf-8")
            with patch(
                "requests.request",
                side_effect=AssertionError("requests.request should not be called"),
            ):
                result = runner.invoke(
                    command,
                    [
                        "run",
                        "demo",
                        "--mode",
                        "preview",
                        "--region",
                        "us-central1",
                        "--config",
                        str(config_path),
                    ],
                    catch_exceptions=False,
                )

            self.assertEqual(result.exit_code, 0, msg=result.output)
            output = result.output
            run_id = _extract_run_id(output)
            self.assertTrue(
                run_id or "summary" in output.lower(),
                msg=f"Expected run_id or summary in output; got: {output}",
            )
            if run_id:
                report_path = Path("runs") / run_id / "report.md"
                self.assertTrue(
                    report_path.is_file(),
                    msg=f"Expected report at {report_path} to exist.",
                )


if __name__ == "__main__":
    unittest.main()
