"""Local-only JSON API for the recruitment workflow. Not a production web service.

python -m tahr.demo_server  # http://127.0.0.1:8765
"""
from __future__ import annotations
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from .workflow import RecruitingWorkspace, WorkflowError
from .integrations import run_mock_sync, MOCK_PROVIDERS

ROOT = Path(__file__).resolve().parents[2]
MAX_BODY_BYTES = 8_192


def make_handler(workspace: RecruitingWorkspace):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            # Never log payloads or candidate details. The server is local-only.
            pass
        def send_json(self, data: dict, status: int = 200):
            payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('X-Frame-Options', 'DENY')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.end_headers()
            self.wfile.write(payload)
        def do_GET(self):
            path = urlsplit(self.path).path
            if path == '/api/health':
                return self.send_json({'status': 'ok', 'mode': 'local-synthetic-training'})
            if path == '/api/workspace':
                return self.send_json(workspace.snapshot())
            if path == '/api/mock/providers':
                return self.send_json({'mock_only': True, 'sample_payloads': MOCK_PROVIDERS})
            if path in ('/', '/index.html'):
                data = (ROOT / 'demo/index.html').read_bytes()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(data)))
                self.send_header('Content-Security-Policy', "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; form-action 'self'")
                self.send_header('X-Content-Type-Options', 'nosniff')
                self.send_header('Cache-Control', 'no-store')
                self.end_headers()
                return self.wfile.write(data)
            return self.send_json({'error': 'Not found'}, 404)
        def do_POST(self):
            path = urlsplit(self.path).path
            if path not in ('/api/requisitions', '/api/requisitions/approve', '/api/applications',
                            '/api/applications/advance', '/api/interviews', '/api/mock/sync'):
                return self.send_json({'error': 'Not found'}, 404)
            if not self.headers.get('Content-Type', '').lower().startswith('application/json'):
                return self.send_json({'error': 'Content-Type must be application/json'}, 415)
            try:
                raw_length = self.headers.get('Content-Length', '')
                if not raw_length.isdigit():
                    return self.send_json({'error': 'Content-Length required'}, 411)
                length = int(raw_length)
                if length > MAX_BODY_BYTES:
                    return self.send_json({'error': 'Payload too large'}, 413)
                value = json.loads(self.rfile.read(length))
                if not isinstance(value, dict):
                    raise WorkflowError('Expected a JSON object')
                if path == '/api/requisitions':
                    result = workspace.create_requisition(value['title'], value['department'],
                                                         value['budget_usd'], value['requestor'])
                elif path == '/api/requisitions/approve':
                    result = workspace.approve_requisition(value['req_id'], value['approver'])
                elif path == '/api/applications':
                    result = workspace.create_application(value['req_id'], value['source'], value['actor'])
                elif path == '/api/applications/advance':
                    result = workspace.advance_application(value['app_id'], value['stage'], value['actor'], value.get('reason', ''))
                elif path == '/api/interviews':
                    result = workspace.schedule_interview(value['app_id'], value['scheduled_at'], value['interviewer'], value.get('mode','Video'))
                else:
                    result = run_mock_sync(workspace, value['provider'], value['payload'])
                return self.send_json({'ok': True, 'result': result}, 201)
            except (WorkflowError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
                # No stack traces; no incoming payloads are echoed to the client.
                return self.send_json({'ok': False, 'error': str(exc) if not isinstance(exc, KeyError) else 'Missing required field'}, 400)
    return Handler


def serve(host='127.0.0.1', port=8765):
    if host not in ('127.0.0.1', 'localhost'):
        raise RuntimeError('This untrusted training API is loopback-only; it is not authenticated')
    with ThreadingHTTPServer((host, port), make_handler(RecruitingWorkspace())) as server:
        print(f'Local-only synthetic training API: http://{host}:{port}')
        server.serve_forever()

if __name__ == '__main__':
    serve()
