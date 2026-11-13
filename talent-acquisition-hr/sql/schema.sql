PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS requisitions (
    req_id TEXT PRIMARY KEY, department TEXT NOT NULL, job_title TEXT NOT NULL,
    owner TEXT NOT NULL, employment_type TEXT NOT NULL, location_type TEXT NOT NULL,
    priority TEXT NOT NULL, opened_at TEXT NOT NULL, closed_at TEXT,
    status TEXT NOT NULL CHECK(status IN ('Open','Filled','Cancelled')),
    approved_budget_usd INTEGER NOT NULL CHECK(approved_budget_usd > 0),
    headcount_approved INTEGER NOT NULL CHECK(headcount_approved > 0),
    business_justification TEXT NOT NULL,
    CHECK ((status = 'Open' AND closed_at IS NULL) OR (status <> 'Open' AND closed_at IS NOT NULL)),
    CHECK (closed_at IS NULL OR closed_at >= opened_at)
);
CREATE TABLE IF NOT EXISTS applications (
    application_id TEXT PRIMARY KEY, candidate_id TEXT NOT NULL, req_id TEXT NOT NULL REFERENCES requisitions(req_id),
    source TEXT NOT NULL, applied_at TEXT NOT NULL, current_stage TEXT NOT NULL
        CHECK(current_stage IN ('Applied','Screened','Interview','Final','Offer','Hired','Rejected','Withdrawn')),
    disposition_reason TEXT, consent_to_contact TEXT NOT NULL CHECK(consent_to_contact IN ('Yes','No')),
    UNIQUE(candidate_id, req_id)
);
CREATE TABLE IF NOT EXISTS stage_events (
    event_id TEXT PRIMARY KEY, application_id TEXT NOT NULL REFERENCES applications(application_id),
    stage TEXT NOT NULL CHECK(stage IN ('Applied','Screened','Interview','Final','Offer','Hired')),
    occurred_at TEXT NOT NULL, actor TEXT NOT NULL,
    UNIQUE(application_id, stage)
);
CREATE TABLE IF NOT EXISTS offers (
    offer_id TEXT PRIMARY KEY, application_id TEXT NOT NULL UNIQUE REFERENCES applications(application_id),
    extended_at TEXT NOT NULL, decision_at TEXT,
    decision TEXT NOT NULL CHECK(decision IN ('Accepted','Declined','Pending')),
    base_pay_usd INTEGER NOT NULL CHECK(base_pay_usd > 0)
);
CREATE TABLE IF NOT EXISTS employees (
    employee_id TEXT PRIMARY KEY, department TEXT NOT NULL, job_family TEXT NOT NULL, level TEXT NOT NULL,
    hire_date TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('Active','Exited')),
    termination_date TEXT, location_type TEXT NOT NULL, employment_type TEXT NOT NULL,
    annual_salary_usd INTEGER NOT NULL CHECK(annual_salary_usd > 0),
    origin_application_id TEXT REFERENCES applications(application_id),
    CHECK((status = 'Exited' AND termination_date IS NOT NULL)
      OR (status = 'Active' AND termination_date IS NULL))
);
CREATE TABLE IF NOT EXISTS onboarding_tasks (
    task_id TEXT PRIMARY KEY, application_id TEXT NOT NULL REFERENCES applications(application_id),
    task_name TEXT NOT NULL, owner_team TEXT NOT NULL, due_at TEXT NOT NULL,
    completed_at TEXT, status TEXT NOT NULL CHECK(status IN ('Open','Completed')),
    CHECK ((status = 'Completed' AND completed_at IS NOT NULL)
      OR (status = 'Open' AND completed_at IS NULL))
);
CREATE TABLE IF NOT EXISTS hr_cases (
    case_id TEXT PRIMARY KEY, employee_id TEXT NOT NULL REFERENCES employees(employee_id),
    category TEXT NOT NULL, priority TEXT NOT NULL, opened_at TEXT NOT NULL,
    closed_at TEXT, status TEXT NOT NULL CHECK(status IN ('Open','Resolved')),
    assigned_team TEXT NOT NULL, resolution_code TEXT,
    CHECK ((status = 'Resolved' AND closed_at IS NOT NULL)
      OR (status = 'Open' AND closed_at IS NULL))
);
CREATE TABLE IF NOT EXISTS candidate_experience_surveys (
    survey_id TEXT PRIMARY KEY, application_id TEXT NOT NULL UNIQUE REFERENCES applications(application_id),
    rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5), responded_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS hiring_manager_surveys (
    response_id TEXT PRIMARY KEY, req_id TEXT NOT NULL UNIQUE REFERENCES requisitions(req_id),
    rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5), responded_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_applications_req ON applications(req_id);
CREATE INDEX IF NOT EXISTS ix_applications_source ON applications(source);
CREATE INDEX IF NOT EXISTS ix_stage_events_stage ON stage_events(stage, occurred_at);
CREATE INDEX IF NOT EXISTS ix_hr_cases_status ON hr_cases(status, opened_at);
CREATE INDEX IF NOT EXISTS ix_req_status ON requisitions(status, department);
