# secure-deployed-AI-system
# Week 9: AI Security and Compliance

## Overview
This week we secured the deployed AfyaPlus AI path: the triage API (`triage_api_v1.py`) and the logistics MCP server (`logistics_mcp.py`). We added secrets handling, encryption at rest, role-based access, an audit trail and data-retention controls. Controls are aligned to the Kenya Data Protection Act as a teaching alignment, not a compliance claim. The manager brief is in `manager_brief.md`.

## Encryption
- transit_ok / TLS evidence: 'transit_policy ok'
- gitignore / resolve_secrets: `.gitignore` covers `.env`, `secrets/` and `logs/`. `secrets_not_in_git.sh` and `check_gitignore.py` fail closed. `resolve_secrets.py` refuses to boot without `JWT_SECRET`. Evidence: `evidence/secrets_not_in_git.txt`, `evidence/secrets_ignored.txt`, `evidence/boot_missing_secret.txt`, `evidence/boot_with_secret.txt`.
- Key Vault or KMS, or the fallback twin JSON: `secret_refs.yaml` points to Azure Key Vault by name. The runnable fallback is `kms_twin.json` with `encrypt_at_rest.py` (library-provided `cryptography.Fernet`, no custom cipher). Production mapping: `docs/key_management_map.json`. Notes: `AT_REST.md`. Evidence: `evidence/encrypt_test.txt`.

## Access control (including MCP)
- rbac.py roles: `partner_clinic` may call `check_stock`. `clinical_ops` may also call `plan_delivery_route`. Unknown roles are denied. Evidence: `evidence/role_matrix.txt`. Known limit: the role is currently a tool argument, not taken from the verified JWT.
- injection_guard: injection_guard OK
- clinic allowlist: `logistics_mcp.py` only answers for IDs in `clinic.json`, returns one clinic per call, and gives generic errors with no list of valid IDs. Evidence: `evidence/mcp_response_sample.txt`.

## Logging
- path to the jsonl: `logs/audit.jsonl` (gitignored). A sample line is in `evidence/audit_sample.jsonl`.
- redact and hash approach: `audit_log.py` redacts Bearer tokens, phone numbers, M-Pesa codes and 8-digit IDs first, then hashes the redacted text. Each line records timestamp, trace ID, actor, action, resource, outcome and payload hash. Free-text names are not caught.

## Kenya DPA
- inventory path: `data_inventory.json`, checked by `check_inventory.py` (`evidence/inventory_check.txt`).
- retention: `retention.json` sets 90 days for messages, audit logs and caller identities, and 30 days for stock queries. `retention_sweep.py` applies it and appends to `deletion_records.jsonl`, which is never swept. The sweep uses a frozen fixture clock, not a production run.
- rights stub / owner: `rights_lookup.py` counts events by peppered subject hash. Owners are named in `RIGHTS.md` (currently placeholders to fill). Erasure is a documented process, not automated.

## Manager brief
See `manager_brief.md`. It has the four required headings: Risks, Mitigations, Kenya DPA alignment, What we will not claim, plus a finance transfer paragraph. The word "unhackable" does not appear (verify with `grep -i unhackable manager_brief_risks.md`, expected no output).

## Fallbacks declared
- [x] no Azure Key Vault (local-env plus the twin JSON)
- [x] no AWS account
- [x] local MCP stub
- [x] legal review pending on lawful_basis

## Checklist
- [x] Secrets not in git
- [x] MCP cannot dump the environment or every clinic
- [x] The brief is readable by a non-engineer