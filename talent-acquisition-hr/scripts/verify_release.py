"""Offline release gate: consistency, artifact presence, archive readability.

Uses Python standard library. This does NOT audit legal or production security compliance.
"""
from __future__ import annotations
import json
import re
import sqlite3
import sys
import zipfile
from xml.etree import ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from tahr.quality import validate
from tahr.metrics import calculate


def main():
    problems=[]
    cfg=json.loads((ROOT/'config/settings.json').read_text())
    expected=calculate(ROOT/'data/processed/talent_hr.sqlite',cfg)
    reported=json.loads((ROOT/'reports/metrics.json').read_text())
    if reported != expected:
        problems.append('metrics.json does not reconcile to SQLite')
    qa=validate(ROOT/'data/processed/talent_hr.sqlite',cfg['snapshot_date'])
    if qa['status']!='PASS':
        problems.append('Data quality failed: '+repr(qa['errors'][:4]))
    if expected['recruiting']['applications'] != 1249:
        problems.append('Unexpected application volume; re-review published documents')
    files=['README.md','reports/dashboard.html','reports/executive_case_study.pdf',
           'templates/Talent_Acquisition_HR_Operations_Workbook.xlsx',
           'assets/dashboard_preview.png','docs/governance/compliance_sources.md',
           'docs/strategy/executive_case_study.md','data/raw/MANIFEST.json']
    for f in files:
        p=ROOT/f
        if not p.is_file() or p.stat().st_size<80:
            problems.append('Missing or empty artifact: '+f)
    dashboard=(ROOT/'reports/dashboard.html').read_text()
    if 'SYNTHETIC DATA ONLY' not in dashboard or '1,249' not in dashboard:
        # The JSON payload uses unformatted 1249, while display formats it in JS.
        if 'SYNTHETIC DATA ONLY' not in dashboard or '"applications": 1249' not in dashboard:
            problems.append('Dashboard disclosure or application data missing')
    if '<script src=' in dashboard or 'https://' in dashboard:
        problems.append('Offline dashboard unexpectedly references an external script/resource')
    pdf=ROOT/'reports/executive_case_study.pdf'
    if pdf.read_bytes()[:4] != b'%PDF':
        problems.append('Executive PDF signature missing')
    workbook=ROOT/'templates/Talent_Acquisition_HR_Operations_Workbook.xlsx'
    with zipfile.ZipFile(workbook) as z:
        if z.testzip():
            problems.append('Workbook ZIP CRC failure')
        ns='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
        sheetxml=[n for n in z.namelist() if n.startswith('xl/worksheets/sheet') and n.endswith('.xml')]
        fcount=sum(len(ET.fromstring(z.read(name)).findall('.//'+ns+'f')) for name in sheetxml)
        charts=sum('/charts/chart' in name and name.endswith('.xml') for name in z.namelist())
        if fcount<200 or charts<1 or len(sheetxml)<12:
            problems.append(f'Excel expected >=12 sheets, >=200 formulas and a chart; got {len(sheetxml)}, {fcount}, {charts}')
    for target in re.findall(r'\]\(([^)]+)\)',(ROOT/'README.md').read_text()):
        if not (target.startswith('http') or target.startswith('#')) and not (ROOT/target).exists():
            problems.append('Broken README link: '+target)
    print('Release quality:', 'PASS' if not problems else 'FAIL')
    print('Tables:',qa['table_counts'])
    print('Workbook:',len(sheetxml),'worksheets;',fcount,'formula cells;',charts,'chart')
    print('Artifacts checked:',len(files),'required; QA errors:',qa['error_count'])
    for err in problems:
        print('ERROR:',err)
    if problems:
        sys.exit(2)

if __name__=='__main__':
    main()
