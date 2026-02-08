# Handler Development Guide

This document defines the standard structure and behavior for tool handlers
used by `hc-agent`.

Handlers implement cloud service logic and are invoked by the unified runner.

---

## Handler Responsibilities

A handler must:

- Support both `preview` and `apply` modes
- Construct API request specifications
- Return structured results
- Avoid direct interaction with storage or MCP layers

---

## Function Signature

Handlers follow a consistent signature:

```python
def handler(
    *,
    mode: str,
    args: dict,
    ctx: RunContext,
    run_id: str | None = None
) -> dict:
    ...
```

---

## Preview Mode

In preview mode, handlers must:
- NOT perform real API calls
- Generate API request previews
- Generate signature summaries
- Return a descriptive summary

---

## Apply Mode

In apply mode, handlers:
- Perform real API calls
- Parse response identifiers when possible
- Return minimal outputs and evidence

---

## Return Structure

Handlers return a dictionary containing:
- `summary`: human-readable description
- `result`: structured result data
- `evidence`: minimal execution metadata

Sensitive fields must not appear in any returned data.

---

## Error Handling

Handlers signal errors by raising structured exceptions.

Errors must:
- Include a stable error code
- Include a clear summary
- Provide remediation hints where possible

---

## Determinism

Handlers should avoid nondeterministic behavior.
- Resource naming should be stable
- Selection logic should be explicit
- Defaults should be resolved outside the handler when possible

---

## Separation of Concerns

Handlers must not:
- Read or write run storage directly
- Handle approval logic
- Perform policy checks
- Perform interactive prompting

These responsibilities belong to the runner and gateway layers.
