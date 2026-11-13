# Raw source fields, keys and modeling decisions

Every record is generated with a deterministic seed and must be interpreted as **fictional**. CSVs are synthetic and deliberately exclude personal names, dates of birth, addresses, contact details, medical information, background results, identity documents and actual protected category values.

## Requisitions — one approved headcount slot per row

**Primary key:** `req_id`. Fields: `department`, `job_title`, `owner`, `employment_type`, `location_type`, `priority`, `opened_at` (ISO date), `closed_at` (nullable ISO date), `status` (Open / Filled / Cancelled), `approved_budget_usd` (positive integer), `headcount_approved` (positive integer), `business_justification` (simulated).

Open requisitions have no close date. Closed reqs have a close date on/after open. This model assumes one approved headcount per req. Production systems may support multiple openings and reopened req histories.

## Applications — one candidate-to-requisition submission per row

**Primary key:** `application_id`; parent: `req_id`. Fields: `candidate_id` (synthetic), `source` (single channel), `applied_at`, `current_stage` (Applied, Screened, Interview, Final, Offer, Hired, Rejected, Withdrawn), `disposition_reason` (neutral categorical reason), `consent_to_contact` (Yes/No). `candidate_id + req_id` is unique in demo. A candidate may have multiple applications in a real ATS; this generator creates a new candidate ID for each to simplify exercises.

**Critical limitation:** `consent_to_contact` is a demonstration field, not evidence of valid marketing consent under any particular law. Real candidate data needs notice, lawful basis, purpose restrictions and consent/opt-out flows where required.

## Stage events — event history, not current state

**Primary key:** `event_id`; foreign key: `application_id`. Fields: `stage` (Applied, Screened, Interview, Final, Offer, Hired), `occurred_at`, `actor` (synthetic role label). One stage per application is modeled, in predefined ascending order; repeated interviews, skips, rejections and reversions would require richer event types in production.

## Offers — one formal version per application

**Primary key:** `offer_id`; one-to-one with `application_id`. Fields: `extended_at`, `decision_at` (nullable for pending), `decision` (Accepted / Declined / Pending), `base_pay_usd` (synthetic amount). No real offer letters or employee payment details. In real operations, amendments, rescissions, multiple offers and legal approval evidence would require separate event/version models.

## Employees — synthetic HRIS roster grain

**Primary key:** `employee_id`. Fields: `department`, `job_family`, `level`, `hire_date`, `status` (Active / Exited), `termination_date` (nullable), `location_type`, `employment_type`, `annual_salary_usd` (fabricated), `origin_application_id` (nullable reference to hired ATS application). This is a point-in-time roster with limited history; it is insufficient for legally required reporting, FTE measures, employee turnover inference or equitable-pay analysis.

## Onboarding tasks — one task and owner per hire

**Primary key:** `task_id`; foreign key: `application_id`. Fields: `task_name`, `owner_team`, `due_at`, `completed_at`, `status`. Task types include welcome, HRIS, payroll/benefits guidance, IT access, 30-day goals, policy acknowledgment and *I-9 handoff only*. No official I-9 documents or verification states appear.

## HR cases — one service request per row

**Primary key:** `case_id`; foreign key: `employee_id`. Fields: `category`, `priority`, `opened_at`, `closed_at`, `status` (Open/Resolved), `assigned_team`, `resolution_code`. It deliberately excludes free-text confidential notes and sensitive attributes; real service desk platforms require more granular confidentiality controls, incident categories and authorized retention.

## Surveys — opt-in response grains

`candidate_experience_surveys`: `survey_id`, `application_id`, `rating` integer 1..5, `responded_at`.

`hiring_manager_surveys`: `response_id`, `req_id`, `rating` integer 1..5, `responded_at`.

Sample selection and nonresponse may distort sentiment results, even if the fake ratings appear favorable. No automated inference about individual attitude or competency is performed.

## Restricted mock voluntary-group file (NOT in warehouse)

`voluntary_group_audit.csv`: `application_id`, `voluntary_group_code` (Group A / B / C / Not disclosed), `data_classification` = RESTRICTED_SYNTHETIC_AUDIT_ONLY. Codes are **not race, gender or any actual protected category**; they only demonstrate the inability of public recruiter dashboards to access restricted audit attributes. `fairness.py` outputs aggregate stage reaches, screening ratios and small-cell suppression. Public GitHub publication would not protect access; future real data would be kept outside Git repositories.

## Missing production concepts (conscious design choices)

The dataset omits separate approved approval signatures, hiring-manager identity, detailed stage rejection events, multiple candidate applications, salary band effective dates, source marketing spend, time-zone/calendar latency, offer versioning, quality-of-hire, voluntary exit reasons, benefits specifics, production MFA and consent logs. These are future-data-model extensions, not falsely completed functionality.
