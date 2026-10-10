# Manager brief: AfyaPlus AI path security

## Risks
- Partner URLs without TLS
- Secrets in git
- Override-style user text
- Unpinned FAQ files
- Over-scoped MCP tools
- Unbounded logs

## Mitigations
- **Secrets in git:** Passwords and keys live outside the code. An automatic check fails if they could be saved to the code history (`secrets_not_in_git.sh`, `.gitignore`, `evidence/secrets_not_in_git.txt`). The system also refuses to start without its signing secret (`resolve_secrets.py`, `evidence/boot_missing_secret.txt`).
- **Stored data readable if stolen:** Sensitive files are encrypted with a vetted library, not a homemade method. The master key is kept apart from the data, with a local stand-in for the cloud key vault (`encrypt_at_rest.py`, `secret_refs.yaml`, `kms_twin.json`, `AT_REST.md`).
- **Over-scoped MCP tools:** Each role can use only its own tools, and an unknown role is refused (`rbac.py`, `evidence/role_matrix.txt`). The stock tool answers only for approved clinics and returns one clinic's figures, not everyone's (`logistics_mcp.py`, `clinic.json`, `evidence/mcp_response_sample.txt`).
- **Who did what:** Every tool call leaves a record of who, what, which clinic and the result. Phone numbers, ID numbers and login tokens are removed before anything is saved (`audit_log.py`, `evidence/audit_sample.jsonl`).
- **Unbounded logs:** Each kind of data has a keep-for period. A cleanup job removes older records and keeps a permanent note of what it removed (`retention.json`, `retention_sweep.py`, `deletion_records.jsonl`).
- **Not yet backed by a file from this week:**
  - *Partner URLs without TLS:* there is no artefact yet. It needs a check that rejects non-HTTPS partner addresses.
  - *Override-style user text:* the input guard that rejects such text before any AI or tool call is not built yet.
  - *Unpinned FAQ files:* `data_inventory.json` records them as kept in git, but no fingerprint check exists yet.

## Kenya DPA alignment
This maps our controls to the ideas in the Kenya Data Protection Act. It is a teaching alignment, not legal advice.
- **Know what we hold and why:** `data_inventory.json` lists messages, caller identities, stock queries and audit logs, each with a purpose. Patient messages are marked as sensitive health data.
- **Keep it no longer than needed:** `retention.json` sets 90 days for messages, audit logs and caller identities, and 30 days for stock queries. `retention_sweep.py` applies the rule.
- **Protect it:** `encrypt_at_rest.py`, `rbac.py` and `audit_log.py` (see Mitigations).
- **People can ask what we hold and ask for deletion:** `rights_lookup.py` counts events about a clinic without exposing content. `RIGHTS.md` names who handles access and erasure requests. Erasure is a documented process, not automated.
- **Reasons for using data:** the lawful-basis labels in `data_inventory.json` are marked "teaching" and need review by a qualified person.

## What we will not claim
- That we are compliant with the Kenya Data Protection Act. We claim alignment of specific controls only.
- Any regulator registration or approval number. None is held or shown.
- That the encryption is deployed in Azure. It runs on a local stand-in. Azure is the production target (`docs/key_management_map.json`).
- That erasure is automated.
- That the roles are tamper-proof. A caller currently states its role. The next step is to take it from the verified login token.
- That removing personal details catches everything. It covers phone numbers, ID numbers, payment codes and tokens, not names in free text.
- That the three unevidenced risks above are fixed.

## Finance transfer
The same pattern applies if this system is reused for a lender or finance team, with one firm rule for credit: the AI recommends, and a person decides. The triage tool already works this way. It gives advisory urgency bands and does not make the care decision. In credit, the AI would give a suggested outcome and the reasons behind it. A named staff member would make the approve-or-decline decision and own it. Every recommendation and every human decision would be written to the audit trail (`audit_log.py`). Applicants' data would be kept only for a set period (`retention.json`) and could be requested or deleted (`RIGHTS.md`). The Act gives people protections against decisions made only by automated means, so a person must be able to ask for human review. Check the exact wording of that provision with a legal reviewer before you present it.