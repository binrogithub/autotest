# One-Click Demo Guide

This document explains the built-in demo orchestration provided by `hc-agent`.

The demo is designed for:
- Customer proof-of-concept
- Internal demonstrations
- AI-driven automation experiments

---

## Demo Overview

The demo executes three cloud operations in sequence:

1. Network
   - Create a security group
2. Storage
   - Create an OBS bucket
3. Compute
   - Create an ECS instance

All steps share a single execution context and `run_id`.

---

## Execution Modes

### Preview Mode

- No real cloud resources are created
- API requests are generated and summarized
- Used for validation and explanation

### Apply Mode

- Real resources are created
- Requires explicit approval
- Uses the same plan generated in preview

---

## Execution Flow

1. Demo is started in preview mode
2. A `run_id` is generated
3. Each step is evaluated sequentially
4. A consolidated report is produced
5. Apply mode reuses the same plan

---

## Output Artifacts

Each demo run generates:

- `plan.json`
- `apply.json`
- `evidence.json`
- `report.md`

Artifacts are stored in the run store and exposed via MCP resources.

---

## Deterministic Behavior

- Resource naming uses a run-specific suffix
- Default network resources are resolved deterministically
- Repeated runs in the same environment produce consistent results

---

## Failure Handling

- Execution stops at the first failed step
- Partial results are preserved
- Reports clearly indicate which step failed
