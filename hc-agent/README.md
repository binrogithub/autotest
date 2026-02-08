# hc-agent

**hc-agent** is a lightweight, AI-first Huawei Cloud automation framework that works with **CLI** and **MCP (Model Context Protocol)**.
It is designed for **PoC, demos, and AI-driven operations**, focusing on **preview/apply safety**, **deterministic automation**, and **low learning cost for both humans and AI agents**.

---

## Goals

- ✅ Make Huawei Cloud **easy to call by AI agents**
- ✅ Provide **safe preview → explicit apply** execution model
- ✅ Keep **CLI simple and stable**, without breaking existing usage
- ✅ Enable **MCP-native orchestration** for LLMs and open-source models
- ✅ Produce **auditable, customer-readable reports** automatically

---

## Core Concepts

### 1. Preview / Apply Model (Mandatory Safety Gate)

All write operations follow the same flow:

1. **preview**
   - No real API calls
   - Returns API request preview + signature hash
   - Generates a `run_id`
2. **apply**
   - Requires `run_id`
   - Requires explicit approval token
   - Requires safety acknowledgement

This makes every operation:
- Predictable
- Auditable
- AI-safe

---

### 2. Unified Runner Envelope

All tools return the same structure:

```json
{
  "ok": true,
  "stage": "preview | apply",
  "run_id": "RUN-xxxx",
  "summary": "Human readable summary",
  "steps": [],
  "result": {},
  "evidence": {},
  "error": null,
  "next_actions": []
}
```

This guarantees:
- CLI and MCP behave identically
- AI never needs to guess response formats

---

### 3. MCP-First Design

AI does not call individual cloud services directly.

Instead, AI calls fixed MCP tools:

| Tool | Purpose |
| --- | --- |
| `hc_tools_search` | Discover available tools |
| `hc_run` | Run a single tool (preview/apply) |
| `hc_run_demo` | Run demo orchestration |
| `hc_doctor_fix` | Auto-resolve missing parameters |

This prevents tool explosion and simplifies reasoning.

---

## Demo Orchestration (Built-in)

`hc_run_demo` runs a real 3-tool chain:

1. **network**
   - Create Security Group
2. **storage**
   - Create OBS bucket
3. **compute**
   - Create ECS instance

All steps:
- Support preview/apply
- Share one `run_id`
- Produce a single report

---

## Configuration (Minimal)

Example `config.yaml`:

```yaml
version: 1

context:
  region: sa-brazil-1
  project_id: xxxx
  non_interactive: true

endpoint:
  use_hcso: false
  base_domain: myhuaweicloud.com
  endpoint_template_public: "{service}.{region}.{base}"

defaults:
  network:
    vpc_id: ""
    subnet_id: ""
    security_group_id: ""

demo:
  compute:
    image_id: ""
    flavor: ""
```

AK/SK are not stored in config.
Use environment variables instead.

---

## Automatic Doctor Fix (Zero-Friction PoC)

When required parameters are missing:
- `hc_doctor_fix` runs automatically
- Applies 3 deterministic rules:
  1. Explicit args / config
  2. Tagged defaults (`hc-agent-default=true`)
  3. Stable tie-break (`ACTIVE` + latest)

Result:
- Fewer questions
- Stable behavior
- AI-friendly

---

## Run Store & Audit

Every run creates:

```
runs/
└─ RUN-xxxx/
   ├─ plan.json
   ├─ apply.json
   ├─ evidence.json
   └─ report.md
```

- Sensitive fields are sanitized
- Reports are customer-readable
- Evidence is minimal but traceable

---

## CLI Usage

Preview:

```bash
hc-agent run demo \
  --mode preview \
  --region sa-brazil-1 \
  --config config.yaml
```

Apply:

```bash
hc-agent run demo \
  --mode apply \
  --run-id RUN-xxxx \
  --approve-token yes \
  --safety-ack I_UNDERSTAND
```

---

## Why CLI Still Exists (Even with MCP)

- CLI is:
  - Deterministic
  - Scriptable
  - Debuggable
- MCP:
  - Reuses the same engine
  - Calls the same runner
  - Produces the same results

One engine, two interfaces.

---

## Design Principles

- No hidden side effects
- No interactive prompts for AI
- No dynamic tool names
- No uncontrolled write access
- No sensitive data in history

---

## Status

This repository represents a PoC-grade but production-shaped architecture.
It is suitable for:
- Customer demos
- AI agent experiments
- Internal platform evolution

---

## License

Internal / PoC use.
Open-sourcing strategy TBD.

---

If you want, **[next I can generate the entire repo (all `.py` + `.md`) as a downloadable zip](chatgpt://followup-prompt?start_index=4269&end_index=4316)**, aligned with this README, implementing a truly "out-of-the-box + AI-ready" experience.
