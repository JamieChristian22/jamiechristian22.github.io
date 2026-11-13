"""Render a compact executive supplement for the verified v2 simulation."""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak
import json

root=Path(__file__).resolve().parents[1]
data=json.loads((root/'reports/advanced_metrics.json').read_text())
out=root/'reports/enterprise_v2_executive_supplement.pdf'
style=getSampleStyleSheet()
style.add(ParagraphStyle(name='Title2',parent=style['Title'],fontSize=20,leading=23,textColor=colors.HexColor('#123650'),spaceAfter=12))
style.add(ParagraphStyle(name='H2v',parent=style['Heading2'],fontSize=12,leading=15,textColor=colors.HexColor('#137b7a'),spaceBefore=16,spaceAfter=7))
style.add(ParagraphStyle(name='HeaderWhite',parent=style['BodyText'],fontSize=8.4,leading=12,textColor=colors.white,fontName='Helvetica-Bold'))
style.add(ParagraphStyle(name='Smallv',parent=style['BodyText'],fontSize=8.4,leading=12))
style.add(ParagraphStyle(name='Memo',parent=style['BodyText'],fontSize=9.2,leading=14,spaceAfter=8))
doc=SimpleDocTemplate(str(out),pagesize=letter,rightMargin=49,leftMargin=49,topMargin=44,bottomMargin=45)
body=[]
def p(txt,sty='Memo'):body.append(Paragraph(txt,style[sty]))
def h(txt):p(txt,'H2v')
def table(head,rows,widths=None):
    t=Table([[Paragraph(str(y),style['HeaderWhite']) for y in head]]+[[Paragraph(str(y),style['Smallv']) for y in row] for row in rows],colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#193a55')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('VALIGN',(0,0),(-1,-1),'TOP'),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#f0f8f9'),colors.white]),('GRID',(0,0),(-1,-1),.25,colors.HexColor('#b9cbd4')),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
    # Explicit paragraph text color white in header to avoid inheriting black.
    body.append(t)

p('Talent Acquisition &amp; HR Operations | Enterprise v2','Title2')
p('<b>Executive portfolio addendum</b> &nbsp; • &nbsp; November 13, 2026 &nbsp; • &nbsp; Fictional enterprise simulation','Smallv')
p('<b>Simulation disclosure:</b> Every candidate, requisition, employee, vendor event and metric is fabricated. This is a portfolio exercise, not a deployed enterprise HR system or actual employer result.')
h('From static analytics to an executable operations case')
p('The v2 upgrade adds a browser-based recruiting workflow, an isolated local training API, two vendor-shaped mock adapters, maturity-aware cohort analytics, audit records and explicit accessibility/security controls. No real candidate decisions or vendor requests occur.')
h('Capabilities and inspectable proof')
table(['Area','Implemented evidence','Key safeguard'],[
('Requisitions','Submit → independent fictional approver → open req','No applicant intake before approval'),
('ATS pipeline','Human stage progression, explicit disposition reason','No scoring / auto-hire'),
('Interview coordination','Future timezone-aware scheduling in local API','No actual calendar invitations'),
('Integrations','Greenhouse-/Workday-shaped local mock mapping','Deduplicate replay; no network calls'),
('People analytics','Monthly cohorts, 60-day maturity, stage lags, fill quartiles','No causal/predictive claims'),
('Quality','17 tests, API negative cases, responsive browser exercise','No real PII or external dependencies')],[107,200,203])
h('Descriptive duration scenario | filled requisitions only')
fill=data['historical_fill_duration_overall']
p(f"n = {fill['filled_reqs']} filled jobs. Illustrative p25 = <b>{fill['p25_days']}</b> days; median = <b>{fill['median_days']}</b> days; p75 = <b>{fill['p75_days']}</b> days. Open and cancelled requisitions are excluded; this is a historical distribution, <b>not</b> a predictive service commitment.")
body.append(PageBreak())
p('Operating recommendations &amp; governance','Title2')
h('Evidence-driven 30 / 60 / 90-day proposal')
table(['Phase','Operating action','Success measures'],[
('Days 1–30','Review intake controls, stage event quality, survey bias and offer decision taxonomy.','Valid requisition brief %, baseline mature-cohort counts'),
('Days 31–60','Pilot feedback service-level agreement; monitor interviews and offer objections by job family.','Median stage wait, manager SLA adherence, decided offers'),
('Days 61–90','Review comparable mature cohorts and assess process reliability; adjust actions on evidence.','Accepted/decided offers, candidate experience, onboarding on-time')],[83,258,169])
h('Security and accessibility decision record')
p('<b>Included:</b> HTML text-safe rendering, labeled fields, keyboard tab navigation, live error messages, responsive layout, reduced motion, bounded JSON payloads, local-only server binding, SQL parameters, mock provider allowlist and stage-state validation.')
p('<b>Not included:</b> production SSO/RBAC, real ATS/HRIS contract integrations, official vendor schema conformance, protected-data processing, verified screen-reader/WCAG 2.2 certification, identity verification, enterprise retention enforcement or a production penetration test.')
h('Demo review path')
p('1. Open <b>demo/index.html</b> offline. 2. Submit and approve a requisition. 3. Create and advance a fictional application. 4. Schedule a mock interview. 5. Import a mock provider event twice to inspect deduplication. 6. Review People Analytics and Governance tabs. 7. Inspect tests and the SQL/data methodology.')
h('Decision and scope')
p('The upgrade demonstrates practical recruiting and HR analytics competencies for interview review. Do not present fictional client outcomes as real employment experience, the mock adapters as official Greenhouse/Workday integrations, or the local training API as production-ready software.')
p('Evidence index: <b>docs/strategy/enterprise_v2_improvement_case.md</b> · <b>docs/technical/mock_integration_contract.md</b> · <b>docs/governance/accessibility_and_security_assessment.md</b> · <b>reports/advanced_metrics.json</b>.','Smallv')
def header_footer(c,d):
 c.saveState();c.setFont('Helvetica',8);c.setFillColor(colors.HexColor('#667b8a'))
 c.drawString(49,28,'Northstar People & Talent — fictional educational portfolio')
 c.drawRightString(letter[0]-49,28,f'Page {d.page}')
 c.restoreState()
doc.build(body,onFirstPage=header_footer,onLaterPages=header_footer)
print(out,out.stat().st_size)
