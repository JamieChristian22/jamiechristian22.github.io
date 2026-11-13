# Offer-to-hire approval checklist — Northstar fictional workflow

## Sample decision packet

**Requisition:** REQ-0001 (filled fictional slot) • **Applicant ID:** recorded in the SQLite source rather than copied to public documents • **Scenario base budget:** from `data/raw/requisitions.csv` • **Authorization:** fictional approval model; no real authority is implied.

| Gate | What must be checked | Accountability | Proof |
| --- | --- | --- | --- |
| Headcount | Req approved, not cancelled/duplicate | Finance / Hiring Manager | req ID and approval log |
| Pay architecture | Compensation and location-specific salary range authorized | Compensation / HRBP | approved band evidence |
| Structured selection | Job-related interview outcome and exceptions signed | Hiring Manager | authorized decision record |
| Conditions | Any checks governed by local/FCRA law | HR Legal | authorized system trail only |
| Candidate contact | Confirm permitted communication channel & timely, accessible notice | Recruiter | ATS message log |
| Signature | Correct human signatories, version and effective date | HR | controlled offer document |
| Decision | Accepted, Declined or Pending with correct timestamps | Recruiter | ATS offer log |
| HRIS handoff | Confirm hire/start and onboard task owners | HR Ops | HRIS joiner record / checklist |

**Do not place signed contracts, actual salary offers, background results, identity documents or candidate contact details in GitHub.** Sample calculations use synthetic `offers.csv`. Acceptance is based on decided (accepted+declined), not pending offers.
