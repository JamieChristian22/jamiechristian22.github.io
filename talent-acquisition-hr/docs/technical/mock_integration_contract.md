# Synthetic integration contract: ATS → recruiting operations

**Status:** executable local training adapter, **not a certified vendor integration**. No Greenhouse, Workday, or other employer/vendor tenant, credentials, API keys, webhook endpoints, or network requests are used. Vendor names describe *illustrative naming conventions*, not an official schema or endorsement.

## Integration boundaries

- `src/tahr/integrations.py`: validates and normalizes sample Greenhouse-shaped and Workday-shaped JSON payloads into a common application record.
- `src/tahr/workflow.py`: imports the normalized record into an isolated in-memory SQLite workspace.
- `(provider, external_id)` is the deduplication key. A replay returns `deduplicated` with the original ID and creates no additional application.
- All applications must belong to an **approved open** requisition; invalid department, missing required field, unknown external provider, malformed dates, missing actor and invalid stage transitions are rejected.
- The server binds to `127.0.0.1` by default. Never expose it on a cloud host; no real authentication, secrets management, transport TLS, monitoring or vendor contractual controls are implemented.

## Example source-to-canonical mapping

| Mock provider | Illustrative source field | Canonical field | Why |
| --- | --- | --- | --- |
| `greenhouse_mock` | `application_id` | `external_id` | Stable replay key |
| `greenhouse_mock` | `job_id` | `req_id` | Match approved requisition |
| `greenhouse_mock` | `channel` | `source` | Aggregate sourcing attribution |
| `workday_mock` | `candidate_application_reference` | `external_id` | Stable replay key |
| `workday_mock` | `requisition_reference` | `req_id` | Match approved requisition |
| `workday_mock` | `source_channel` | `source` | Aggregate sourcing attribution |

### Contract example

```json
{
  "provider": "greenhouse_mock",
  "payload": {
    "application_id": "GH-DEMO-015",
    "job_id": "REQ-D0001",
    "channel": "Careers Site"
  }
}
```

`POST /api/mock/sync` → `{ "ok": true, "result": { "operation": "created", "application_id": "APP-D0010", "external_call_performed": false, ... } }`.

Sending the same request again returns `operation: "deduplicated"`. Changing the provider namespaces the external key. Real production implementations would also check source update timestamps, field-level ownership, immutable audit logs, least-privilege OAuth permissions, retry budgets, API throttling, dead-letter queues, reconciliation checkpoints and webhook signature verification.

## Local API reference

| Method | Route | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Simulation readiness |
| GET | `/api/workspace` | Read fictional requisitions/applications/interviews and recent audit |
| GET | `/api/mock/providers` | Display supported sample payloads |
| POST | `/api/requisitions` | Submit a pending requisition |
| POST | `/api/requisitions/approve` | Require a distinct approver |
| POST | `/api/applications` | Create application under an open requisition |
| POST | `/api/applications/advance` | Transition to next stage or document rejection |
| POST | `/api/interviews` | Schedule a mock event with timezone offset |
| POST | `/api/mock/sync` | Normalize, import and deduplicate mock ATS data |

**Launch:** `PYTHONPATH=src python -m tahr.demo_server` then open `http://127.0.0.1:8765`. HTTP JSON request bodies are capped at 8 KiB. No CORS wildcard is returned. Current HTTP methods only simulate operations: the **GitHub Pages demo is deliberately browser-only**.

## Reconciliation / resilience scenarios

1. Send a valid mock application: expect one new record and an audit event.
2. Replay same external key: expect original application ID, no duplicate.
3. Unknown provider: fail closed.
4. Unknown / unapproved requisition: reject without creating a candidate record.
5. Missing external ID or malformed field: reject with a sanitized error.
6. Retry after any server restart: test workspace intentionally resets. A production sync must persist the dedupe ledger and report that capability separately.

## Technical debt / productization gates

Before any real deployment: move from in-memory to an approved encrypted HR datastore, implement federated SSO and RBAC, enforce server-side action authorization (demo actor labels are **not** authorization), obtain HR/privacy/legal approval, implement retention controls, validate vendor schema and API version, obtain sandbox credentials, complete vendor security review, set retry and backoff policies, and run end-to-end contract tests against authorized vendor sandboxes. Do not upload real PII into the portfolio.
