# MCP Usage Guide

This document describes how `hc-agent` exposes capabilities through the
Model Context Protocol (MCP).

The MCP interface is designed to be **stable, minimal, and AI-friendly**.
It intentionally avoids dynamic or per-service tool exposure.

---

## Design Principles

- Fixed tool surface (no tool explosion)
- Deterministic input and output schemas
- Explicit preview → apply execution model
- Safe for autonomous and semi-autonomous AI agents

---

## Exposed MCP Tools

The MCP server exposes a small, fixed set of tools.

### `hc_tools_search`

Searches available internal tools and returns usage templates.

- Read-only
- No side effects
- Used by AI to discover capabilities

**Output includes:**
- Tool name
- Description
- Risk level
- Example `hc_run` invocation template

---

### `hc_run`

Executes a single cloud operation through the unified runner.

**Supported modes:**
- `preview`: no real API call
- `apply`: real API execution with explicit approval

All write operations must pass through this tool.

---

### `hc_run_demo`

Executes a predefined multi-step demo orchestration.

- Network (security group)
- Storage (OBS bucket)
- Compute (ECS)

All steps share a single `run_id`.

---

### `hc_doctor_fix`

Resolves missing or ambiguous parameters automatically.

- Uses deterministic selection rules
- Does not create resources
- Produces a context patch (`ctx_patch`)

---

## Preview vs Apply

### Preview

- No side effects
- Returns:
  - API request preview
  - Signature hash
  - Execution summary
- Generates a `run_id`

### Apply

- Requires:
  - `run_id`
  - Approval token
  - Safety acknowledgement
- Executes real API calls
- Stores evidence and results

---

## Resources API

MCP resources expose run artifacts.

Common URIs:
- `hc-run://<run_id>/report.md`
- `hc-run://<run_id>/run.json`
- `hc-run://<run_id>/plan.json`
- `hc-run://<run_id>/apply.json`

Resources are read-only and sanitized.

---

## Error Handling

All MCP tools return structured results.

Errors are returned as part of the response envelope, not as protocol-level failures.

This ensures consistent behavior for AI clients.
