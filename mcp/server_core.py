"""Server-side entry points for MCP runs."""

from .run_gateway import hc_run
from .state_store import RunStore


def hc_run_demo(store_dir="./mcp_runs"):
    """Run a demo preview/apply workflow and return the run record."""
    def preview(payload):
        return {"status": "previewed", "payload": payload}

    def apply(payload):
        return {"status": "applied", "payload": payload}

    store = RunStore(store_dir)
    return hc_run(preview, apply, store, payload={"demo": True})
