# Smoke validation script

This repository includes a minimal smoke validation script at
`scripts/smoke_validation.sh`. It avoids heavy test frameworks and is intended
for quick end-to-end checks.

## Prerequisites

* `rg` and `bash` available on the PATH.
* The CLI commands you want to exercise are available, or you can use the
  built-in mock mode for a no-network, no-service run.

## Commands and expected outputs

### 1) Mocked run (no external services)

This mode generates a local `report.md` and uses mock output for the preview
step. It is helpful for confirming the script wiring and output matching.

```bash
SMOKE_USE_MOCK=1 \
MCP_LIST_TOOLS_CMD='printf "tools: [hc_tools_search]\n"' \
HC_TOOLS_SEARCH_CMD='printf "result: []\n"' \
SMOKE_POLICY_BLOCK_CMD='printf "policy blocked for demo\n"; exit 1' \
SMOKE_OPS_APPLY_CMD='printf "apply succeeded for ops\n"' \
./scripts/smoke_validation.sh
```

**Expected output (abridged):**

```
==> Preview (expect run_id + report.md)
run_id: mock-123
report.md: /tmp/.../report.md

==> MCP list_tools
tools: [hc_tools_search]

==> hc_tools_search
result: []

==> Policy block (demo tenant)
policy blocked for demo

==> Apply allowed (ops tenant with approvals)
apply succeeded for ops

==> Smoke validation complete
```

### 2) Real CLI run (replace commands as needed)

Point the script at your real CLI commands. The example below assumes:

* `hc preview` writes a report to the provided path and prints `run_id:`.
* `mcp list_tools` emits `hc_tools_search` in its output.
* `hc_tools_search` emits a `result` key in its output.
* `hc apply` fails with a policy-block message for the demo tenant.
* `hc apply` succeeds for the ops tenant when approvals are provided.

```bash
export SMOKE_REPORT_PATH=/tmp/hc-smoke/report.md
export SMOKE_APPROVALS=/tmp/hc-smoke/approvals.json

SMOKE_PREVIEW_CMD='hc preview --tenant demo --output "$SMOKE_REPORT_PATH"' \
MCP_LIST_TOOLS_CMD='mcp list_tools' \
HC_TOOLS_SEARCH_CMD='hc_tools_search' \
SMOKE_POLICY_BLOCK_CMD='hc apply --tenant demo --plan "$SMOKE_REPORT_PATH"' \
SMOKE_OPS_APPLY_CMD='hc apply --tenant ops --plan "$SMOKE_REPORT_PATH" --approvals "$SMOKE_APPROVALS"' \
./scripts/smoke_validation.sh
```

**Expected output (abridged):**

```
==> Preview (expect run_id + report.md)
run_id: <RUN_ID>
report.md: /tmp/hc-smoke/report.md

==> MCP list_tools
... hc_tools_search ...

==> hc_tools_search
result: ...

==> Policy block (demo tenant)
... policy blocked ...

==> Apply allowed (ops tenant with approvals)
... apply succeeded ...

==> Smoke validation complete
```

## Output matching customization

If your CLI outputs differ, you can adjust expected patterns via environment
variables:

* `SMOKE_MCP_TOOLS_PATTERN` (default: `hc_tools_search`)
* `SMOKE_TOOLS_SEARCH_PATTERN` (default: `result`)
* `SMOKE_POLICY_BLOCK_PATTERN` (default: `policy.*(blocked|denied)`)
* `SMOKE_APPLY_ALLOWED_PATTERN` (default: `apply.*(succeeded|allowed|ok)`)

Example:

```bash
SMOKE_POLICY_BLOCK_PATTERN='blocked by policy' \
SMOKE_APPLY_ALLOWED_PATTERN='status: ok' \
./scripts/smoke_validation.sh
```
