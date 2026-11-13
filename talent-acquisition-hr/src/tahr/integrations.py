"""Vendor-shaped adapters against synthetic inputs; never call vendor services."""
from __future__ import annotations
from .workflow import RecruitingWorkspace, WorkflowError, short_text

# These shapes illustrate integration design only. They DO NOT reproduce official
# vendor schemas, use vendor SDKs, or make authenticated requests.
MOCK_PROVIDERS = {
    'greenhouse_mock': {'application_id': 'GH-DEMO-015', 'job_id': 'REQ-D0001', 'channel': 'Careers Site'},
    'workday_mock': {'candidate_application_reference': 'WD-DEMO-027', 'requisition_reference': 'REQ-D0002',
                     'source_channel': 'Employee Referral'},
}

def normalize(provider: str, payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise WorkflowError('Mock payload must be a JSON object')
    if provider == 'greenhouse_mock':
        keys = ('application_id', 'job_id', 'channel')
    elif provider == 'workday_mock':
        keys = ('candidate_application_reference', 'requisition_reference', 'source_channel')
    else:
        raise WorkflowError('Unknown mock provider')
    missing = [k for k in keys if k not in payload]
    if missing:
        raise WorkflowError('Missing mock fields: ' + ', '.join(missing))
    return {'external_id': short_text(payload[keys[0]], 'external application ID', 48),
            'req_id': short_text(payload[keys[1]], 'requisition ID', 40),
            'source': short_text(payload[keys[2]], 'source', 50)}

def run_mock_sync(workspace: RecruitingWorkspace, provider: str, payload: dict) -> dict:
    normalized = normalize(provider, payload)
    result = workspace.import_external_application(provider, **normalized)
    return {'provider': provider, 'operation': 'created' if result['created'] else 'deduplicated',
            'application_id': result['application']['id'], 'external_id': normalized['external_id'],
            'external_call_performed': False}
