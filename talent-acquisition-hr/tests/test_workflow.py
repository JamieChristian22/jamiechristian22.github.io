"""Functional, security, idempotency, API and analytical regression checks."""
import json
import sys
import threading
import unittest
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from tahr.workflow import RecruitingWorkspace, WorkflowError
from tahr.integrations import run_mock_sync, MOCK_PROVIDERS, normalize
from tahr.advanced_analytics import analyze
from tahr.demo_server import make_handler, MAX_BODY_BYTES


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.w = RecruitingWorkspace()

    def tearDown(self):
        self.w.close()

    def test_requisition_approval_and_separation_of_duties(self):
        req = self.w.create_requisition('Recruiter I', 'People & Culture', 64000, 'Requestor A')
        with self.assertRaises(WorkflowError):
            self.w.create_application(req['id'], 'Careers Site', 'Recruiter A')
        with self.assertRaises(WorkflowError):
            self.w.approve_requisition(req['id'], 'Requestor A')
        self.assertEqual(self.w.approve_requisition(req['id'], 'HRBP B')['status'], 'Open')
        with self.assertRaises(WorkflowError):
            self.w.approve_requisition(req['id'], 'HRBP B')
        self.assertEqual(self.w.create_application(req['id'], 'Careers Site', 'Recruiter A')['stage'], 'Applied')

    def test_valid_stepwise_transition_and_audit(self):
        self.w.advance_application('APP-D0003', 'Screened', 'Reviewer A')
        self.w.advance_application('APP-D0003', 'Interview', 'Reviewer A')
        self.assertEqual(self.w.snapshot()['applications'][2]['stage'], 'Interview')
        self.assertTrue(any(e['action'] == 'stage_advanced' for e in self.w.snapshot()['audit_trail']))
        with self.assertRaises(WorkflowError):
            self.w.advance_application('APP-D0003', 'Hired', 'Reviewer A')

    def test_skipped_stage_and_rejection_rules(self):
        with self.assertRaises(WorkflowError):
            self.w.advance_application('APP-D0003', 'Offer', 'Reviewer A')
        with self.assertRaises(WorkflowError):
            self.w.advance_application('APP-D0003', 'Rejected', 'Reviewer A', '')
        with self.assertRaises(WorkflowError):
            self.w.advance_application('APP-D0003', 'Rejected', 'Reviewer A', 'disability')
        r = self.w.advance_application('APP-D0003', 'Rejected', 'Reviewer A', 'Required certification not verified')
        self.assertEqual(r['stage'], 'Rejected')
        with self.assertRaises(WorkflowError):
            self.w.advance_application('APP-D0003', 'Screened', 'Reviewer A')

    def test_interview_scheduling_with_timezone_and_restrictions(self):
        with self.assertRaises(WorkflowError):
            self.w.schedule_interview('APP-D0003', '2026-10-01T10:00:00Z', 'Panel A')
        with self.assertRaises(WorkflowError):
            self.w.schedule_interview('APP-D0003', (datetime.now(timezone.utc)+timedelta(days=4)).isoformat(), 'Panel A')
        when = (datetime.now(timezone.utc)+timedelta(days=4)).isoformat()
        record = self.w.schedule_interview('APP-D0001', when, 'Panel A')
        self.assertEqual(record['status'], 'Scheduled')
        self.assertEqual(len(self.w.snapshot()['interviews']), 1)

    def test_replay_idempotency_and_provider_mapping(self):
        p = MOCK_PROVIDERS['workday_mock']
        first = run_mock_sync(self.w, 'workday_mock', p)
        again = run_mock_sync(self.w, 'workday_mock', p)
        self.assertEqual(first['operation'], 'created')
        self.assertEqual(again['operation'], 'deduplicated')
        self.assertEqual(first['application_id'], again['application_id'])
        self.assertFalse(first['external_call_performed'])
        with self.assertRaises(WorkflowError):
            normalize('vendor_real', p)
        with self.assertRaises(WorkflowError):
            normalize('greenhouse_mock', {'job_id': 'REQ-D0001'})

    def test_input_bounding_and_hostile_markups_are_data_only(self):
        with self.assertRaises(WorkflowError):
            self.w.create_requisition('x'*200, 'Analytics', 70000, 'Actor')
        with self.assertRaises(WorkflowError):
            self.w.create_requisition('Title', 'Analytics', True, 'Actor')
        with self.assertRaises(WorkflowError):
            self.w.create_requisition('Title', 'Analytics', 70000, 'Actor\nnewline')
        test = self.w.create_requisition('<img src=x onerror=alert(1)>', 'Analytics', 70000, 'Actor')
        # Raw input is stored as data, but HTML display only uses textContent.
        self.assertIn('<img', test['title'])

    def test_advanced_metric_maturity_and_conservation(self):
        report = analyze(ROOT/'data/processed/talent_hr.sqlite', '2026-10-31')
        self.assertEqual(sum(x['applications'] for x in report['application_cohorts']), 1249)
        self.assertEqual(report['historical_fill_duration_overall']['filled_reqs'], 24)
        self.assertTrue(any(not x['mature_60d'] for x in report['application_cohorts']))
        self.assertTrue(all(x['hires'] <= x['applications'] for x in report['application_cohorts']))
        self.assertTrue(all(x['mature_hires'] <= x['mature_applications'] for x in report['source_cohorts_60d']))



class DemoMarkup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tabs = self.panels = self.forms = 0
        self.labels = set()
        self.inputs = set()
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('role') == 'tab': self.tabs += 1
        if a.get('role') == 'tabpanel': self.panels += 1
        if tag == 'form': self.forms += 1
        if tag == 'label' and a.get('for'): self.labels.add(a['for'])
        if tag in ('input','select','textarea') and a.get('id'): self.inputs.add(a['id'])


class DemoSecurityTests(unittest.TestCase):
    def test_accessible_static_structure_and_no_third_party_data_flow(self):
        html = (ROOT/'demo/index.html').read_text()
        parsed = DemoMarkup();parsed.feed(html)
        self.assertEqual(parsed.tabs, parsed.panels)
        self.assertGreaterEqual(parsed.tabs, 5)
        self.assertEqual(parsed.forms, 3)
        self.assertTrue(parsed.inputs.issubset(parsed.labels))
        self.assertIn('aria-live="polite"', html)
        self.assertIn('prefers-reduced-motion:reduce', html)
        self.assertIn('Skip to main content', html)
        self.assertIn('textContent', html)
        self.assertNotIn('fetch(', html)
        self.assertNotIn('https://', html)
        self.assertNotIn('/*ADVANCED_JSON*/', html)
        self.assertIn('connect-src \'self\'', html)

    def test_local_json_api_contract_no_wildcard_cors(self):
        workspace=RecruitingWorkspace()
        server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(workspace))
        worker=threading.Thread(target=server.serve_forever,daemon=True)
        worker.start()
        base=f'http://127.0.0.1:{server.server_address[1]}'
        def call(path, body=None, method=None, content_type='application/json'):
            payload=None if body is None else json.dumps(body).encode()
            req=Request(base+path, data=payload, method=method or ('POST' if payload is not None else 'GET'), headers={'Content-Type':content_type})
            try:
                with urlopen(req,timeout=5) as response:
                    return response.status,json.loads(response.read()),dict(response.headers)
            except HTTPError as e:
                return e.code,json.loads(e.read()),dict(e.headers)
        try:
            status,body,headers=call('/api/health')
            self.assertEqual(status,200)
            self.assertNotIn('Access-Control-Allow-Origin', headers)
            self.assertEqual(headers['X-Content-Type-Options'], 'nosniff')
            status,body,_=call('/api/applications/advance',{'app_id':'APP-D0003','stage':'Hired','actor':'Test'})
            self.assertEqual(status,400)
            status,body,_=call('/api/requisitions',{'title':'HR Analyst','department':'Analytics','budget_usd':62000,'requestor':'Manager'})
            self.assertEqual(status,201)
            self.assertEqual(body['result']['status'],'Pending Approval')
            status,_,_=call('/api/mock/sync',{'provider':'real_greenhouse','payload':{}})
            self.assertEqual(status,400)
            status,_,_=call('/api/something-invalid',{'x':1})
            self.assertEqual(status,404)
            status,_,_=call('/api/requisitions',{'x':1},content_type='text/plain')
            self.assertEqual(status,415)
            self.assertLess(MAX_BODY_BYTES,10000)
        finally:
            server.shutdown();server.server_close();workspace.close();worker.join(timeout=2)

if __name__ == '__main__':
    unittest.main()
