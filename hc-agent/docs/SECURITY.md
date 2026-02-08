# Security Model

This document describes how `hc-agent` handles security, data protection,
and operational risk.

---

## Credential Handling

- Access keys and secrets are never stored in run artifacts
- Credentials should be provided via environment variables
- Configuration files do not contain sensitive information

---

## Preview Safety

- Preview mode does not perform real API calls
- No cloud state is modified during preview
- Signature material is stored only as cryptographic hashes

---

## Data Sanitization

All stored data passes through a sanitization layer.

Sanitized fields include:
- Tokens
- Authorization headers
- Certificates
- Private keys
- Kubeconfig content

Large or sensitive values are replaced with hashes or redacted markers.

---

## Evidence Minimization

Only minimal execution evidence is stored:

- Service name
- Endpoint
- HTTP method
- Request path
- Status code
- Request ID
- Duration
- Signature hash

Request bodies, headers, and credentials are never stored.

---

## Auditability

Each run produces immutable artifacts:

- Execution plan
- Apply results
- Sanitized evidence
- Human-readable report

These artifacts allow post-run analysis without exposing sensitive data.

---

## Risk Control

- All write operations require explicit approval
- Preview and apply are strictly separated
- Tenant-level policies can restrict write access

---

## Multi-Tenant Isolation

- Each run is associated with a tenant identifier
- Tenant context is injected server-side
- Policies control which tools and actions are allowed
