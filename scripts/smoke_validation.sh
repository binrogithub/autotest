#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
WORK_DIR=${SMOKE_WORK_DIR:-$(mktemp -d)}
REPORT_PATH=${SMOKE_REPORT_PATH:-"$WORK_DIR/report.md"}

MCP_LIST_TOOLS_CMD=${MCP_LIST_TOOLS_CMD:-"mcp list_tools"}
HC_TOOLS_SEARCH_CMD=${HC_TOOLS_SEARCH_CMD:-"hc_tools_search"}
PREVIEW_CMD=${SMOKE_PREVIEW_CMD:-"hc preview --tenant demo --output $REPORT_PATH"}
POLICY_BLOCK_CMD=${SMOKE_POLICY_BLOCK_CMD:-"hc apply --tenant demo --plan $REPORT_PATH"}
OPS_APPLY_CMD=${SMOKE_OPS_APPLY_CMD:-"hc apply --tenant ops --plan $REPORT_PATH --approvals $SMOKE_APPROVALS"}

MCP_TOOLS_PATTERN=${SMOKE_MCP_TOOLS_PATTERN:-"hc_tools_search"}
TOOLS_SEARCH_PATTERN=${SMOKE_TOOLS_SEARCH_PATTERN:-"result"}
POLICY_BLOCK_PATTERN=${SMOKE_POLICY_BLOCK_PATTERN:-"policy.*(blocked|denied)"}
APPLY_ALLOWED_PATTERN=${SMOKE_APPLY_ALLOWED_PATTERN:-"apply.*(succeeded|allowed|ok)"}

log() {
  printf '\n==> %s\n' "$1"
}

run_cmd() {
  local cmd=$1
  bash -c "$cmd"
}

capture_cmd() {
  local cmd=$1
  local output
  output=$(bash -c "$cmd" 2>&1)
  printf '%s' "$output"
}

assert_contains() {
  local label=$1
  local output=$2
  local pattern=$3

  if ! printf '%s\n' "$output" | rg -q --pcre2 "$pattern"; then
    printf '\n[ERROR] %s: expected output to match /%s/\n' "$label" "$pattern" >&2
    return 1
  fi
}

assert_file() {
  local path=$1
  if [[ ! -f "$path" ]]; then
    printf '\n[ERROR] expected file not found: %s\n' "$path" >&2
    return 1
  fi
}

parse_run_id() {
  local output=$1
  printf '%s\n' "$output" | sed -n 's/.*run_id[:=][[:space:]]*\([A-Za-z0-9._-]\+\).*/\1/p' | head -n1
}

run_preview() {
  log "Preview (expect run_id + report.md)"

  if [[ ${SMOKE_USE_MOCK:-0} -eq 1 ]]; then
    mkdir -p "$(dirname "$REPORT_PATH")"
    cat <<'MOCK' > "$REPORT_PATH"
# Mock report

- status: ok
MOCK
    printf 'run_id: mock-123\nreport.md: %s\n' "$REPORT_PATH"
    return 0
  fi

  local output
  output=$(capture_cmd "$PREVIEW_CMD")
  printf '%s\n' "$output"

  local run_id
  run_id=$(parse_run_id "$output")
  if [[ -z "$run_id" ]]; then
    printf '\n[ERROR] missing run_id in preview output\n' >&2
    return 1
  fi

  assert_file "$REPORT_PATH"
}

run_mcp_list_tools() {
  log "MCP list_tools"

  local output
  output=$(capture_cmd "$MCP_LIST_TOOLS_CMD")
  printf '%s\n' "$output"
  assert_contains "list_tools" "$output" "$MCP_TOOLS_PATTERN"
}

run_hc_tools_search() {
  log "hc_tools_search"

  local output
  output=$(capture_cmd "$HC_TOOLS_SEARCH_CMD")
  printf '%s\n' "$output"
  assert_contains "hc_tools_search" "$output" "$TOOLS_SEARCH_PATTERN"
}

run_policy_block_demo() {
  log "Policy block (demo tenant)"

  local output
  set +e
  output=$(capture_cmd "$POLICY_BLOCK_CMD")
  local status=$?
  set -e

  printf '%s\n' "$output"

  if [[ $status -eq 0 ]]; then
    printf '\n[ERROR] expected demo tenant apply to fail\n' >&2
    return 1
  fi

  assert_contains "policy block" "$output" "$POLICY_BLOCK_PATTERN"
}

run_ops_apply() {
  log "Apply allowed (ops tenant with approvals)"

  local output
  output=$(capture_cmd "$OPS_APPLY_CMD")
  printf '%s\n' "$output"

  assert_contains "ops apply" "$output" "$APPLY_ALLOWED_PATTERN"
}

main() {
  log "Working directory: $WORK_DIR"
  log "Report path: $REPORT_PATH"

  run_preview
  run_mcp_list_tools
  run_hc_tools_search
  run_policy_block_demo
  run_ops_apply

  log "Smoke validation complete"
}

main "$@"
