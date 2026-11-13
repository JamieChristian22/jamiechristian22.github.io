# Solution architecture, lineage and data contract

## Problem and operating context

Northstar is a fictitious 6-department organization that needs the core data disciplines expected in enterprise recruiting and HR Operations: controlled requisition approvals, candidate stage traceability, offers, onboarding, employee roster, service cases, feedback measurement, and auditable management reporting.

### Component responsibilities

| Component | Input | Output | Owner | Control |
| --- | --- | --- | --- | --- |
| Generator | Random seed + fiction assumptions | 9 raw CSVs + mock restricted audit CSV | Data engineering | Fixed seed and schema |
| Loader | CSV and SQL schema | SQLite relational warehouse | HRIS/Analytics | FK, enums, date and uniqueness constraints |
| Validator | Warehouse | `data_quality.json` | Data governance | Hard fail on invalid event history |
| Metric layer | Warehouse + `config/settings.json` | `metrics.json` | People Analytics | Consistent denominator definitions |
| Audit layer | Restricted mock group codes + warehouse IDs | Aggregate fairness screen only | Compliance | No candidate-level joined export; small cell suppression |
| HTML report | `metrics.json` | self-contained interactive dashboard | Reporting | Only non-sensitive aggregates; no network calls |
| Excel workbook | CSVs, metrics, templates | formula-linked operational workbook | Recruiting Operations | Editable controls and source reconciliation |
| PDF report | `metrics.json` | manager-ready case study | TA/HR leadership | Label every finding as simulated |
| Automated tests | generator, DB and dashboards | CI green/red | Repository maintainer | deterministic regeneration and negative validation tests |

## Logical data grain

| Table | Grain (one row per...) | Primary ID | Key foreign relationship |
| --- | --- | --- | --- |
| `requisitions` | approved req/headcount slot | `req_id` | root |
| `applications` | an application to a requisition | `application_id` | `req_id` |
| `stage_events` | stage reached by application | `event_id` | `application_id` |
| `offers` | one formal offer per app (demo design) | `offer_id` | `application_id` |
| `employees` | HRIS employee record | `employee_id` | optional `origin_application_id` |
| `onboarding_tasks` | one task per hired application | `task_id` | `application_id` |
| `hr_cases` | one employee service request | `case_id` | `employee_id` |
| `candidate_experience_surveys` | one returned candidate survey | `survey_id` | `application_id` |
| `hiring_manager_surveys` | one survey per filled req | `response_id` | `req_id` |

Stage reach is an **event**; current status is a **current-state attribute**. A rejected candidate may have reached Interview, and thus is present in the Interview funnel. A candidate can apply to multiple reqs in a real ATS; demo IDs are one-to-one for interpretability, not a recommended enterprise ID convention. Multiple offers per candidate/requisition would require relaxing the offer uniqueness model in a production adaptation.

## Sensitivity separation

`data/restricted/voluntary_group_audit.csv` is deliberately absent from the SQLite warehouse and standard dashboard. A candidate-application key is used only transiently inside `fairness.py` for aggregated review. That script reports codes named Group A, B and C to avoid implying actual EEO identity classification, does not publish row-level joins and suppresses small cells. A proper production adaptation needs policy-approved secure storage, a lawful basis, aggregate access rules, specialist legal review and an approved demographic data taxonomy.

## Key transformation and quality checks

1. Ingest fields in their declared row grain with stable IDs.
2. Reject broken FK relationships, unexpected statuses, duplicate stage events or missing applied events.
3. Validate stage order Applied > Screened > Interview > Final > Offer > Hired and nondecreasing dates.
4. Validate lifecycle alignment: exactly one hire per filled requisition in this single-headcount simulation, and accepted offers for those hires.
5. Validate employee linkage, HR case dates, onboarding linkage and no future-dated records beyond snapshot.
6. Use inclusive/explicit sample rules for HR case SLA and onboarding deadlines, and document pending offer exclusion.
7. Record data quality status; refuse to present metrics if validation fails during `demo`.

## Production extension decision register (NOT implemented)

- **Security:** SSO/OIDC, MFA, scoped permissions, database encryption, secrets manager, audit logs, PII minimization and DLP scanning.
- **Integrations:** vendor-specific ATS/HRIS API contracts, pagination, rate limits, retries, idempotent ingestion, field mapping and consent checks.
- **Reliability:** nightly snapshot/CDC extraction, checksums, quarantine zone, incremental merges, monitored tasks, alerting and disaster recovery.
- **Privacy:** data processing agreements, regional storage, data subject request process, legal holds, lawful retention and documented deletion.
- **Analytics:** event sourcing, consistent cohort accounting, historical snapshots, source cost ROI, approved employee start date, req aging, role-level comparability and confidence intervals.
- **Governance:** human-only candidate decisions, accessibility review, structured interview calibration, independent audit oversight and remediation action tracking.

This repository is a *portfolio-ready reference implementation*, not production software or a deployed multi-user ATS.
