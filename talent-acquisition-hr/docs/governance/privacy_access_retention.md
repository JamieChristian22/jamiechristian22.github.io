# Privacy engineering, role separation, retention and security model

## Classification (demo + real-world future controls)

| Data class | Example | Allowed location in demo | Production recommendation |
| --- | --- | --- | --- |
| PUBLIC_SYNTHETIC | invented job req IDs, stage events, employee IDs, aggregates | CSV, SQLite, workbook, HTML, GitHub | May publish only after confirming fake content and no copied personal information |
| RESTRICTED_SYNTHETIC_AUDIT_ONLY | fictional Group A/B/C voluntary codes | `data/restricted/` and aggregate audit only | Separate EEO vault with legal basis, minimum access, anti-join protection |
| CONFIDENTIAL_PERSONNEL | actual compensation, case notes, resumes, performance, contact info | **NEVER in this repository** | Encrypted approved ATS/HRIS; scoped roles, retention, breach and lawful access policy |
| HIGHLY_RESTRICTED | actual I-9 documents, medical/accommodation, consumer reports, SSNs | **NEVER in this repository** | Specific authorized systems with legal retention, audit access, secure deletion and holds |

## Least-privilege role model

| Role | Requisition | Candidate process info | Employee HRIS | HR service cases | Voluntary audit data |
| --- | --- | --- | --- | --- | --- |
| Hiring manager | assigned requisitions | assigned applications / structured interview evidence | team-approved limited access | no, except authorized own request | **none** |
| Recruiter | assigned jobs | approved candidate process fields | joiner status only | none | **none** |
| TA Ops analyst | operational requisition stats | pseudo-ID / aggregated pipeline, as needed | no raw personnel data | only aggregate handoff metrics | **none** |
| HR Ops agent | joiner tasks only | hire-hand-off only | authorized staff workflows | assigned need-to-know | **none** |
| People Analytics | aggregated role/date fields | approved pseudonymized analytical views | restricted reporting dataset | secure reporting views | aggregated approved report only |
| Compliance / Privacy specialist | audit access | authorized investigation scope | scope-approved | restricted case scope | legal-approved audit access |
| Platform admin | configuration / availability | no routine business access by default | no routine business access | no routine business access | no routine business access |

## Controls in code versus controls a real corporation must add

**Built and testable:** synthetic-only data; no direct identifying fields; separate audit file; no group data in SQLite; no automatic scoring; row grain documented; referential checks; source control CI; isolated dashboard aggregates; optional read-only SQL dashboard connection.

**Not implemented, do not claim:** RBAC authentication, encryption at rest, SSO, audit log retention, background check integration, live email delivery, vendor APIs, deletion request workflows, cloud-hosted secrets, malware scanning of resumes, tenant isolation, HIPAA protections or legal archiving.

## Retention design steps for production

1. Inventory all data categories and sources; record who controls them and their lawful purposes.
2. Assign a jurisdiction-/record-type-specific retention policy after counsel review, not a one-size-fits-all value.
3. Track start event and stop event for retention clocks; identify exceptions, employee disputes and litigation holds.
4. Build a review queue for eligible deletion and evidence of execution; never auto-delete holds or protected records.
5. Define system of record, data lineage and export controls; prevent email attachments and public GitHub copies of employee records.
6. Train TA, HR, payroll, IT and analytics owners on privacy incidents, DSAR routing and minimum-necessary access.

## Data breach / privacy issue response

Immediately contain access, preserve a minimal authorized incident trail, alert Security and Privacy, evaluate system and data scope, engage legal on notification duties, document remediation and re-test access. Do not publish actual impacted information as a GitHub issue.

## Pre-publication gate

Search files for `@`, realistic names/addresses, actual customer and employee records, credentials, `.env` files, resume attachments, signed offers, protected-class values and image/medical materials. Verify that samples were programmatically invented. Separate public code from any real internal data permanently.
