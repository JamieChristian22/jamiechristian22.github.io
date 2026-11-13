"""Isolated, reversible talent operations training workspace.

No PII, real employees, external calls, or automatic candidate decisions.
Roles in this demo label the workflow; they are NOT authentication.
"""
from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Any

DEPARTMENTS = ("Analytics", "Engineering", "Finance & Operations", "People & Culture", "Product", "Customer Success")
STAGES = ("Applied", "Screened", "Interview", "Final", "Offer", "Hired")
TRANSITIONS = {a: b for a, b in zip(STAGES, STAGES[1:])}

class WorkflowError(ValueError):
    """An action violates the process contract."""


def short_text(value: Any, field: str, limit: int = 90) -> str:
    if not isinstance(value, str):
        raise WorkflowError(f"{field} must be text")
    value = value.strip()
    if not value or len(value) > limit or any(ord(c) < 32 for c in value):
        raise WorkflowError(f"{field} must be 1–{limit} printable characters")
    return value


def iso_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class RecruitingWorkspace:
    """In-memory by default: refresh/restart safely resets the exercise."""
    def __init__(self, filename: str = ":memory:", seed: bool = True):
        self.lock = threading.RLock()
        self.db = sqlite3.connect(filename, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys = ON")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS demo_requisitions (
            id TEXT PRIMARY KEY, title TEXT NOT NULL, department TEXT NOT NULL,
            budget_usd INTEGER NOT NULL CHECK(budget_usd BETWEEN 30000 AND 500000),
            status TEXT NOT NULL CHECK(status IN ('Pending Approval','Open','Closed')),
            requestor TEXT NOT NULL, approver TEXT, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS demo_applications (
            id TEXT PRIMARY KEY, req_id TEXT NOT NULL REFERENCES demo_requisitions(id),
            source TEXT NOT NULL, stage TEXT NOT NULL, disposition_reason TEXT,
            created_at TEXT NOT NULL, UNIQUE(id, req_id));
        CREATE TABLE IF NOT EXISTS demo_interviews (
            id TEXT PRIMARY KEY, app_id TEXT NOT NULL REFERENCES demo_applications(id),
            scheduled_at TEXT NOT NULL, interviewer TEXT NOT NULL, mode TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Scheduled');
        CREATE TABLE IF NOT EXISTS demo_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT NOT NULL,
            actor TEXT NOT NULL, action TEXT NOT NULL, entity_id TEXT NOT NULL,
            detail TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS demo_external_ids (
            provider TEXT NOT NULL, external_id TEXT NOT NULL, app_id TEXT NOT NULL,
            PRIMARY KEY(provider, external_id));
        """)
        self.db.commit()
        if seed and not self.db.execute("SELECT 1 FROM demo_requisitions LIMIT 1").fetchone():
            self._seed()

    def close(self):
        self.db.close()

    def _next(self, table: str, prefix: str) -> str:
        n = self.db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] + 1
        return f"{prefix}{n:04d}"

    def _audit(self, actor: str, action: str, entity_id: str, detail: dict | None = None):
        self.db.execute("INSERT INTO demo_audit(timestamp,actor,action,entity_id,detail) VALUES(?,?,?,?,?)",
                        (iso_utc(), short_text(actor, 'actor'), action, entity_id, json.dumps(detail or {}, sort_keys=True)))

    def _seed(self):
        for title, dept, budget in [
            ("Talent Acquisition Specialist", "People & Culture", 78000),
            ("People Analytics Analyst I", "Analytics", 85000),
            ("Cloud Support Engineer I", "Engineering", 92000),
            ("HR Operations Coordinator", "People & Culture", 62000)]:
            req = self.create_requisition(title, dept, budget, "Hiring Manager (demo)")
            self.approve_requisition(req['id'], 'HRBP (demo)')
        for req_id, sources in [("REQ-D0001", ["Employee Referral", "Careers Site", "LinkedIn"]),
                                ("REQ-D0002", ["Job Board", "Careers Site"]),
                                ("REQ-D0003", ["Employee Referral", "Job Board"]),
                                ("REQ-D0004", ["Careers Site", "LinkedIn"])]:
            for src in sources:
                self.create_application(req_id, src, "Recruiter (demo)")
        self.advance_application("APP-D0001", "Screened", "Recruiter (demo)")
        self.advance_application("APP-D0001", "Interview", "Recruiter (demo)")
        self.advance_application("APP-D0002", "Screened", "Recruiter (demo)")
        self.advance_application("APP-D0004", "Screened", "Recruiter (demo)")

    def _row(self, table: str, pk: str) -> sqlite3.Row:
        r = self.db.execute(f"SELECT * FROM {table} WHERE id=?", (pk,)).fetchone()
        if not r:
            raise WorkflowError("Record not found")
        return r

    def create_requisition(self, title: str, department: str, budget_usd: int, requestor: str) -> dict:
        title = short_text(title, "job title")
        if department not in DEPARTMENTS:
            raise WorkflowError("Select a listed department")
        if isinstance(budget_usd, bool) or not isinstance(budget_usd, int) or not 30000 <= budget_usd <= 500000:
            raise WorkflowError("Approved budget request must be $30,000–$500,000")
        requestor = short_text(requestor, "requestor")
        with self.lock, self.db:
            req = self._next('demo_requisitions', 'REQ-D')
            self.db.execute('INSERT INTO demo_requisitions VALUES(?,?,?,?,?,?,?,?)',
                            (req, title, department, budget_usd, 'Pending Approval', requestor, None, iso_utc()))
            self._audit(requestor, 'requisition_submitted', req, {'department': department})
            return dict(self._row('demo_requisitions', req))

    def approve_requisition(self, req_id: str, approver: str) -> dict:
        approver = short_text(approver, 'approver')
        with self.lock, self.db:
            r = self._row('demo_requisitions', req_id)
            if r['status'] != 'Pending Approval':
                raise WorkflowError('Only pending requisitions may be approved')
            if approver.casefold() == r['requestor'].casefold():
                raise WorkflowError('Requester and approver must be different in the demo')
            self.db.execute('UPDATE demo_requisitions SET status=?, approver=? WHERE id=?', ('Open', approver, req_id))
            self._audit(approver, 'requisition_approved', req_id)
            return dict(self._row('demo_requisitions', req_id))

    def create_application(self, req_id: str, source: str, actor: str) -> dict:
        source = short_text(source, 'source', 50)
        actor = short_text(actor, 'actor')
        with self.lock, self.db:
            req = self._row('demo_requisitions', req_id)
            if req['status'] != 'Open':
                raise WorkflowError('Applications require an approved open requisition')
            app = self._next('demo_applications', 'APP-D')
            self.db.execute('INSERT INTO demo_applications VALUES(?,?,?,?,?,?)',
                            (app, req_id, source, 'Applied', None, iso_utc()))
            self._audit(actor, 'application_logged', app, {'req_id': req_id, 'source': source})
            return dict(self._row('demo_applications', app))

    def advance_application(self, app_id: str, new_stage: str, actor: str, reason: str = '') -> dict:
        actor = short_text(actor, 'reviewer')
        with self.lock, self.db:
            row = self._row('demo_applications', app_id)
            old = row['stage']
            if new_stage == 'Rejected':
                if old in ('Rejected', 'Withdrawn', 'Hired'):
                    raise WorkflowError('Closed applications cannot be changed')
                reason = short_text(reason, 'job-related disposition reason', 160)
                if 'protected' in reason.casefold() or 'disability' in reason.casefold():
                    raise WorkflowError('Use a documented job-related reason, never a protected characteristic')
                self.db.execute('UPDATE demo_applications SET stage=?, disposition_reason=? WHERE id=?', ('Rejected', reason, app_id))
            elif TRANSITIONS.get(old) == new_stage:
                if new_stage == 'Interview':
                    pass
                if new_stage == 'Hired':
                    raise WorkflowError('A hire requires a documented accepted offer; demo has no auto-hire action')
                self.db.execute('UPDATE demo_applications SET stage=? WHERE id=?', (new_stage, app_id))
            else:
                raise WorkflowError('Invalid stage transition; follow the approved sequence')
            self._audit(actor, 'candidate_disposition' if new_stage == 'Rejected' else 'stage_advanced',
                        app_id, {'from': old, 'to': new_stage, 'reason': reason if new_stage == 'Rejected' else ''})
            return dict(self._row('demo_applications', app_id))

    def schedule_interview(self, app_id: str, when: str, interviewer: str, mode: str = 'Video') -> dict:
        interviewer = short_text(interviewer, 'interviewer')
        if mode not in ('Video', 'Phone', 'On-site'):
            raise WorkflowError('Unsupported interview mode')
        try:
            dt = datetime.fromisoformat(when.replace('Z', '+00:00'))
            if dt.tzinfo is None:
                raise ValueError('offset required')
            if dt.astimezone(timezone.utc) <= datetime.now(timezone.utc):
                raise ValueError('interview must be future dated')
        except (ValueError, AttributeError) as e:
            raise WorkflowError('Use a future ISO timestamp with a timezone offset') from e
        with self.lock, self.db:
            app = self._row('demo_applications', app_id)
            if app['stage'] != 'Interview':
                raise WorkflowError('Schedule only applications at Interview stage')
            i_id = self._next('demo_interviews', 'INT-D')
            self.db.execute('INSERT INTO demo_interviews(id,app_id,scheduled_at,interviewer,mode) VALUES(?,?,?,?,?)',
                            (i_id, app_id, dt.isoformat(), interviewer, mode))
            self._audit(interviewer, 'interview_scheduled', i_id, {'app_id': app_id, 'mode': mode})
            return dict(self._row('demo_interviews', i_id))

    def import_external_application(self, provider: str, external_id: str, req_id: str, source: str, actor: str = 'Mock sync') -> dict:
        if provider not in ('greenhouse_mock', 'workday_mock'):
            raise WorkflowError('Only explicit local mock providers are supported')
        external_id = short_text(external_id, 'external_id', 48)
        with self.lock, self.db:
            mapping = self.db.execute('SELECT app_id FROM demo_external_ids WHERE provider=? AND external_id=?',
                                      (provider, external_id)).fetchone()
            if mapping:
                return {'application': dict(self._row('demo_applications', mapping['app_id'])), 'created': False}
            app = self.create_application(req_id, source, actor)
            self.db.execute('INSERT INTO demo_external_ids VALUES(?,?,?)', (provider, external_id, app['id']))
            return {'application': app, 'created': True}

    def snapshot(self) -> dict:
        with self.lock:
            def rows(table: str, order: str = 'id') -> list[dict]:
                return [dict(row) for row in self.db.execute(f'SELECT * FROM {table} ORDER BY {order}').fetchall()]
            return {'label': 'SYNTHETIC DATA / NOT A PRODUCTION ATS OR HRIS',
                    'requisitions': rows('demo_requisitions'),
                    'applications': rows('demo_applications'),
                    'interviews': rows('demo_interviews'),
                    'audit_trail': rows('demo_audit', 'id DESC')[:30]}
