# People Operations / HRIS service delivery playbook

**Scenario owner:** HR Operations Manager • **Business environment:** 188 active synthetic staff across six functions; 150 synthetic HR service tickets. This is a simulated internal service model, not a production employee platform.

## Case intake and handling lifecycle

1. **Intake:** Receive an employee/manager request through an approved confidential HR service channel. Create case ID; log category, minimum description, impacted business service, priority, received date and response owner. Do not copy health, benefits claims, medical leaves or protected personal information into generic analytics systems.
2. **Triage:** Check urgency and statutory dependency. High priority means time-sensitive employee impact; referrals involving protected leave, workplace safety or legal claims go to authorized specialists immediately.
3. **Verify authorization:** Restrict access by role and data classification. HR service agents can view only case details needed for their authorized task. Identity verification must use approved company mechanisms, not questions that disclose secrets.
4. **Investigate:** Compare reported issue to approved policy, employee lifecycle status and relevant service records; use cited source of truth. Document decisions and seek HRBP/Payroll/Legal approval as needed.
5. **Resolve:** Communicate factual next steps, record a neutral resolution code, confirm the requested action is completed and close the ticket with timestamp.
6. **Review and improve:** Reopen incorrect resolutions; record control failures and the associated change request. Aggregate repeat contacts and service categories without publishing individual case contents.

### SLA design in this portfolio

- Fictional default target: **5 calendar days** from ticket `opened_at` to `closed_at` for a resolved ticket.
- On-time resolution percentage = resolved within 5 calendar days / all resolved cases.
- Open overdue ticket = open case older than 5 calendar days as of snapshot.
- No claim is made that this is a legal requirement or industry benchmark. Real HR cases may require different rules, especially statutory/leave/benefits/payroll issues.
- An open-case age alert does not trigger auto-closure. Human owner reviews and documents status.

## Functional runbooks

| Case family | First resolver | Required evidence / boundary | Escalation trigger |
| --- | --- | --- | --- |
| HRIS Access | HRIS + IAM | Role entitlement, approval, access ticket | Excessive privilege, breach, missing owner |
| Payroll Question | Payroll | Approved pay code, period, payroll statement in secured payroll system | Underpayment, taxation, compliance deadline |
| Benefits Guidance | Benefits team | Plan literature; eligibility reviewed in authorized system | Coverage lapse, privacy concern |
| Leave Routing | Leave/HRBP | Direct to protected case management, not generic notes | FMLA, ADA, accommodation or confidential medical information |
| Policy Clarification | HRBP | Current company policy and effective date | Conflicting policies, employee complaint |
| Manager Support | HRBP | Manager authorization and objective facts | Employee relations investigation or conflict of interest |

## HRIS governance: joins, moves, exits

### Joiner (accepted hire -> active employee)

Verify approved start date, HRIS master record, unique employee ID, employment classification, reporting manager, correct department, authorized system access and documented payroll/benefits handoff. Reconcile ATS accepted offer vs HRIS start and resolve differences. Route I-9 to employer's approved process: the demo records handoff only.

### Mover (internal transfer/promotion)

Require approved manager and HRBP change, effective date, pay/level review, least-privilege access adjustment, retained manager history as applicable and communication plan. Never update historical requisition records silently to make the transaction appear on time.

### Leaver (voluntary/involuntary termination)

Use confidential authorized case workflow, record effective separation date, payroll/benefits follow-up, equipment return, time-bound access shutdown, legal hold/records retention controls. Confirm legal review for final pay requirements and leave/benefits effects. Public reporting should use aggregate counts only.

## Onboarding service control (seven milestone model)

1. Welcome and first-day logistics — Recruiting Ops.
2. HRIS profile verification — People Operations.
3. Payroll/benefits guidance — People Operations.
4. Equipment/access provisioning — IT.
5. Role-specific 30-day goals — Hiring Manager.
6. Policy acknowledgment — People Operations.
7. I-9 process handoff — People Operations through authorized employer process.

Do **not** collect or store identity docs or I-9 forms in a public project. Every task has a due date and completion evidence, and the on-time metric includes incomplete due tasks in the denominator.

## Monthly people-ops review

Look for unresolved case backlog, late onboarding tasks, repeat contact rate, data sync errors, role-based access issues, separation completion delays and feedback. Use this fictional project to practice triage and stakeholder communication; never infer live employee sentiment or sensitive attributes from the synthetic dataset.
