"""Generate the portfolio's polished, data-backed executive PDF from metrics.json.

Optional dependency: pip install -r requirements-reports.txt
"""
from __future__ import annotations
import json
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.graphics.shapes import Drawing, Rect, String, Line

ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/"reports/metrics.json").read_text())
r=DATA['recruiting']; p=DATA['people_operations']
OUT=ROOT/"reports/executive_case_study.pdf"
NAVY=HexColor('#122F47'); TEAL=HexColor('#0B7D88'); MIST=HexColor('#EDF4F6')
SLATE=HexColor('#35566B'); AMBER=HexColor('#C68B2C'); INK=HexColor('#213746'); PALE=HexColor('#F5F8FA')
WHITE=colors.white
font='/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
fontbold='/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
pdfmetrics.registerFont(TTFont('Corp',font))
pdfmetrics.registerFont(TTFont('Corp-Bold',fontbold))
pdfmetrics.registerFontFamily('Corp',normal='Corp',bold='Corp-Bold')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='CoverKickerX',fontName='Corp-Bold',fontSize=11,leading=14,textColor=TEAL,spaceAfter=10))
styles.add(ParagraphStyle(name='CoverTitleX',fontName='Corp-Bold',fontSize=34,leading=39,textColor=NAVY,spaceAfter=15))
styles.add(ParagraphStyle(name='CoverIntroX',fontName='Corp',fontSize=12,leading=18,textColor=SLATE,spaceAfter=20))
styles.add(ParagraphStyle(name='HeadingX',fontName='Corp-Bold',fontSize=17,leading=22,textColor=NAVY,spaceBefore=0,spaceAfter=12))
styles.add(ParagraphStyle(name='SubheadX',fontName='Corp-Bold',fontSize=11.7,leading=16,textColor=TEAL,spaceBefore=13,spaceAfter=8))
styles.add(ParagraphStyle(name='BodyX',fontName='Corp',fontSize=9.4,leading=14.5,textColor=INK,spaceAfter=9))
styles.add(ParagraphStyle(name='SmallX',fontName='Corp',fontSize=8,leading=11.7,textColor=SLATE,spaceAfter=7))
styles.add(ParagraphStyle(name='TableHeadX',fontName='Corp-Bold',fontSize=8,leading=10,textColor=WHITE))
styles.add(ParagraphStyle(name='TableBodyX',fontName='Corp',fontSize=8,leading=11,textColor=INK))
styles.add(ParagraphStyle(name='StatX',fontName='Corp-Bold',fontSize=26,leading=30,textColor=TEAL))
styles.add(ParagraphStyle(name='StatLabelX',fontName='Corp',fontSize=8,leading=11,textColor=SLATE))

def P(txt,style='BodyX'):
    return Paragraph(txt,styles[style])

def T(rows,widths=None,header=True,pad=8):
    rows=[[v if isinstance(v,Paragraph) else P(str(v),'TableHeadX' if i==0 and header else 'TableBodyX') for v in row] for i,row in enumerate(rows)]
    t=Table(rows,colWidths=widths,repeatRows=1 if header else 0,hAlign='LEFT')
    cmds=[('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),pad),('RIGHTPADDING',(0,0),(-1,-1),pad),
          ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),7),
          ('LINEBELOW',(0,-1),(-1,-1),.4,HexColor('#D9E4E9'))]
    if header:
        cmds += [('BACKGROUND',(0,0),(-1,0),NAVY),('ROWBACKGROUNDS',(0,1),(-1,-1),[WHITE,PALE])]
    else:
        cmds += [('ROWBACKGROUNDS',(0,0),(-1,-1),[WHITE,PALE])]
    t.setStyle(TableStyle(cmds));return t

def bar_drawing(items,total_width=465,row_h=28,bar_limit=290,value_suffix=''):
    d=Drawing(total_width,row_h*len(items)+13)
    maximum=max([val for _,val in items] or [1])
    for j,(name,value) in enumerate(items):
        y=row_h*(len(items)-1-j)+7
        d.add(String(0,y+7,name,fontName='Corp',fontSize=8.5,fillColor=SLATE))
        d.add(Rect(148,y+2,bar_limit,11,fillColor=MIST,strokeColor=None,rx=3,ry=3))
        d.add(Rect(148,y+2,max(1,bar_limit*value/maximum),11,fillColor=TEAL,strokeColor=None,rx=3,ry=3))
        d.add(String(454,y+5,f'{value:,}{value_suffix}',fontName='Corp-Bold',fontSize=8,fillColor=NAVY,textAnchor='end'))
    return d

def header_footer(c,doc):
    w,h=letter
    c.saveState()
    c.setFillColor(NAVY);c.rect(0,h-24,w,24,fill=1,stroke=0)
    c.setFont('Corp-Bold',8);c.setFillColor(WHITE);c.drawString(43,h-16,'NORTHSTAR  /  TALENT & PEOPLE OPERATIONS')
    c.setFont('Corp',8);c.setFillColor(SLATE)
    c.line(43,40,w-43,40)
    c.drawString(43,27,'FICTIONAL BUSINESS CASE  |  SYNTHETIC DATA ONLY  |  2026-10-31')
    c.drawRightString(w-43,27,f'{doc.page}')
    c.restoreState()

doc=SimpleDocTemplate(str(OUT),pagesize=letter,rightMargin=43,leftMargin=43,topMargin=52,bottomMargin=53,title='Talent Acquisition and HR Operations | Northstar Simulated Executive Case Study',author='Talent and HR Operations Portfolio',subject='Synthetic corporate recruiting and HR data analytics case study')
story=[]
# Page 1 - executive brief.
story.extend([Spacer(1,17),P('EXECUTIVE PORTFOLIO CASE STUDY  /  2026','CoverKickerX'),
    P('Talent acquisition<br/>that scales. People<br/>operations that deliver.','CoverTitleX'),
    P('An evidence-first corporate operations simulation: full requisition-to-hire workflow, structured hiring, HR service controls, onboarding accountability and explainable analytics.','CoverIntroX')])
stat_table=T([[P('42','StatX'),P('1,249','StatX'),P('204','StatX')],
              [P('Approved requisitions','StatLabelX'),P('Synthetic applications','StatLabelX'),P('Synthetic employee records','StatLabelX')]],
             widths=[176,176,174],header=False,pad=10)
stat_table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),MIST),('BOX',(0,0),(-1,-1),.4,MIST),('TOPPADDING',(0,0),(-1,0),15),('BOTTOMPADDING',(0,-1),(-1,-1),15)]))
story+=[stat_table,Spacer(1,22),P('THE MANAGEMENT PROBLEM','SubheadX'),
 P('The scenario has 24 filled, 12 open and 6 cancelled requisitions. Filled roles take <b>56.2 calendar days</b> on average against a fictional 45-day target. Only <b>24 of 77 decided offers (31.2%)</b> are accepted. HR onboarding and service workflows also fall below internal goals. The portfolio explores what leaders could test, how they should monitor it and what compliance safeguards they must retain.'),
 P('PORTFOLIO DISCLOSURE','SubheadX'),
 P('<b>Not a real employer, client, candidate pool or historical consulting engagement.</b> Every record is generated from a fixed random seed. Identifiers, activities, budgets, scores and findings are fictional. The case is not an approved ATS, HRIS, I-9 workflow, candidate scoring model or legal compliance certification.','SmallX'),
 P('Technology: Python + SQL/SQLite + Excel + offline HTML + optional Streamlit + automated data-quality tests.','SmallX'),PageBreak()]

# Page 2 - KPI and interpretation.
story.extend([P('01  |  Leadership scorecard','HeadingX'),
 P('From approved headcount to staff service delivery, this is a deterministic October 31, 2026 snapshot. Targets are scenario assumptions - not universal HR benchmarks.'),
 T([['Measure','Simulated observation','Fictional target / readout'],
    ['Requisitions','24 filled / 12 open / 6 cancelled','42 total, 1 approved HC each'],
    ['Mean time to fill',f"{r['time_to_fill_days']['mean']} days; n=24",'45 days; target missed by 11.2 days'],
    ['Mean time to hire',f"{r['time_to_hire_days']['mean']} days; n=24",'30 days; on target in scenario'],
    ['Offer acceptance',f"{r['offers']['acceptance_pct']}%; 24 / 77 decided",'85% target; 12 pending excluded'],
    ['Candidate survey favorable',f"{r['candidate_experience']['favorable_pct']}%; n=311",'24.9% response rate; nonresponse bias'],
    ['Onboarding on time',f"{p['onboarding']['on_time_pct_of_due']}%; 103 / 168 due",'90% target; 15 overdue open tasks'],
    ['HR service resolved in SLA',f"{p['hr_service_cases']['sla_pct_of_resolved']}%; 63 / 131 resolved",'5 calendar day scenario SLA; 19 open overdue']], [155,146,225]),
 Spacer(1,14),P('Priority decisions','SubheadX'),
 T([['Priority','Business intervention hypothesis','Owner / test'],
    ['P0','Review approval lead time and declined offers; do not assume compensation is the sole driver.','TA lead + compensation; decision / reason trail'],
    ['P0','Assign start-readiness owner and escalate late handoffs before day one.','HR operations + IT; due-task compliance'],
    ['P1','Triage overdue HR tickets by category, priority and authorization.','HR Ops; overdue aging and resolved SLA'],
    ['P1','Instrument stage aging and panel-debrief waits to find scheduling bottlenecks.','Recruiting Ops; role/cohort-stratified stages']], [48,290,188]),
 Spacer(1,9),P('Management caution: a low ratio does not establish causation. All effect sizes, cost savings and proposed uplift remain unmeasured until an intervention is actually piloted.','SmallX'),PageBreak()])

# Page 3 - recruiting deep dive.
story.extend([P('02  |  Recruiting funnel and sourcing','HeadingX'),
 P('Stage reach is a cumulative event count. A rejected applicant can have completed several stages; funnel bars therefore represent <b>ever-reached</b> stages, not mutually exclusive current statuses.'),
 P('Stage attainment (all 1,249 applications)','SubheadX'),
 bar_drawing([(x['stage'],x['reached']) for x in r['funnel']]),
 Spacer(1,13),P('Source mix: descriptive, not attribution of return on spend','SubheadX'),
 T([['Source','Applications','Hires','Raw hire %']]+[[x['source'],x['applicants'],x['hires'],f"{x['hire_conversion_pct']}%"] for x in r['source_performance']], [230,100,78,118]),
 Spacer(1,14),P('Why we would not cut a source based on these rates','SubheadX'),
 P('Applications span differently aged requisitions. The model lacks source costs, job-family normalization, campaign duration and the counterfactual of how these same candidates might have performed through another channel. A responsible next step is to create mature requisition cohorts, reconcile source capture, validate costs and review small samples before reallocating budget.'),
 P('Applicant fairness control','SubheadX'),
 P('No automated ranking or demographic selection is used. Mock group codes are audited separately, in aggregate only. Human selection must be job-related, consistent and accessible.','SmallX'),PageBreak()])

# Page 4 - people ops.
story.extend([P('03  |  People Operations delivery','HeadingX'),
 P(f"The fictional employee roster contains <b>{p['headcount']['active']} active</b> and <b>{p['headcount']['exited_in_roster']} exited-in-roster</b> records. The exited count is not an annual turnover measure."),
 P('HR service case volumes by category','SubheadX'),
 bar_drawing([(x['category'],x['total']) for x in p['hr_service_cases']['by_category']]),
 Spacer(1,14),P('Service reliability and onboarding evidence','SubheadX'),
 T([['Operational measure','Observed','Interpretation / action'],
    ['Cases resolved',f"{p['hr_service_cases']['resolved']} of {p['hr_service_cases']['total']}",'Count open cases separately; do not treat open tickets as resolved.'],
    ['Resolved within 5 calendar days',f"{p['hr_service_cases']['resolved_within_sla']} / {p['hr_service_cases']['resolved']}",'A fictional service goal, not a statutory mandate.'],
    ['Open overdue cases',p['hr_service_cases']['overdue_open'],'Accountable human triage and access-aware routing.'],
    ['Onboarding due tasks',p['onboarding']['due_by_snapshot'],'Seven milestone types for each completed hire.'],
    ['Completed on/before due',p['onboarding']['completed_on_time'],'Incomplete due tasks remain in denominator.'],
    ['Overdue open onboarding',p['onboarding']['overdue_open'],'Prioritize blocked start/readiness items.']], [175,110,241]),
 Spacer(1,14),P('What to implement first','SubheadX'),
 P('Put task ownership and required completion dates in a shared approved HR workflow. Escalate start-blocking IT and HR items with a defined accountable owner. For case handling, create a daily priority queue and maintain separate secure workflows for leave, medical/accommodation, payroll-sensitive and legal cases. Do not use an ordinary SLA to delay urgent statutory obligations.'),
 P('I-9 boundary: the demo tracks only an employer process handoff. It contains no documents, verification results or employee eligibility statuses.','SmallX'),PageBreak()])

# Page 5 - plan.
story.extend([P('04  |  30 / 60 / 90-day change roadmap','HeadingX'),
 P('Operating change requires accountable ownership, clear leading indicators and a process to stop or revise interventions that worsen fairness, privacy or candidate experience.'),
 T([['Phase','Deliverables','Owner / acceptance evidence'],
    ['Days 1-30','Validate req ownership, classify offer issues, map candidate response delays, triage cases, and publish approved KPI definitions.','TA Ops / Comp / HR Ops; data-quality gate and signed process decisions.'],
    ['Days 31-60','Pilot offer pre-approval review, new-hire start-readiness coordination, and service-case category routing.','TA / HR / IT; monitor elapsed time and overdue rate; no claims of achieved lift.'],
    ['Days 61-90','Compare mature cohorts, review controlled outcomes, document privacy impact, train owners and decide keep, revise or roll back.','People Analytics / HR Legal / leadership; signed results and limitation memo.']], [95,232,199]),
 Spacer(1,20),P('Decision rights and exception flow','SubheadX'),
 T([['Situation','Accountable workflow','Escalation'],
    ['Job/comp change after posting','Manager + HRBP + TA sign-off','Legal review if criteria or legal postings change'],
    ['Potential discriminatory / inaccessible process','Job-related and accessible human review','Immediate HR Legal / Privacy escalation'],
    ['Offer delay or approval mismatch','Recruiter + Compensation','TA lead; hold offer until authorized'],
    ['Blocked employee start','HR Ops coordinator + IT','Same-day blocker review and owner assignment'],
    ['Metric discrepancy or future-dated event','People Analytics / Data Owner','Stop report release until validator passes']], [155,178,193]),
 Spacer(1,19),P('How to measure success without overclaiming','SubheadX'),
 P('Use comparable requisition cohorts, explicit eligibility windows, sample counts and documented definitions. A change in offer acceptance cannot be credited to an intervention until alternative explanations, sample maturity and selection effects are reviewed. Document monitoring for adverse impacts, consent and data minimization in each pilot.','BodyX'),PageBreak()])

# Page 6 - architecture and sources.
story.extend([P('05  |  Operating system and governance','HeadingX'),
 P('This portfolio is executable and inspectable, not merely an outline. The generator creates candidate and HRIS transactions; SQLite enforces foreign keys and enum/date checks; a Python validator checks lifecycle consistency; metrics feed offline HTML and an Excel operations workbook. Optional Streamlit reads the SQLite warehouse.'),
 T([['Evidence asset','Why a hiring manager or HR leader should care'],
    ['reports/dashboard.html','Zero-dependency presentation with department view and explainable KPI summaries.'],
    ['templates/Talent_Acquisition_HR_Operations_Workbook.xlsx','Operational rows, dropdowns, formulas, case / onboarding fields, interviewer example.'],
    ['sql/schema.sql + sql/analytics.sql','Relational model, integrity constraints and transparent, reusable SQL questions.'],
    ['src/tahr/ + tests/','Reproducible synthesis, KPI logic, group separation, data contract and negative tests.'],
    ['docs/operations/ + docs/strategy/','Detailed recruiting/HR SOPs, RACI, business case and change-control roadmap.'],
    ['docs/governance/','Official-source links, privacy/access design, AI selection guardrails and risks.']], [210,316]),
 Spacer(1,13),P('Official reference authorities - checked 2026-11-13','SubheadX'),
 P('EEOC Employment Tests: <link href="https://www.eeoc.gov/laws/guidance/employment-tests-and-selection-procedures" color="#0B7D88">eeoc.gov/laws/guidance/employment-tests-and-selection-procedures</link>','SmallX'),
 P('FTC/EEOC Background Checks: <link href="https://www.ftc.gov/business-guidance/resources/background-checks-what-employers-need-know" color="#0B7D88">ftc.gov/business-guidance/resources/background-checks-what-employers-need-know</link>','SmallX'),
 P('USCIS I-9 Central: <link href="https://www.uscis.gov/i-9" color="#0B7D88">uscis.gov/i-9</link>  |  EEOC Recordkeeping: <link href="https://www.eeoc.gov/employers/recordkeeping-requirements" color="#0B7D88">eeoc.gov/employers/recordkeeping-requirements</link>','SmallX'),
 P('NIST AI Risk Management Framework: <link href="https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10" color="#0B7D88">nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10</link>','SmallX'),
 Spacer(1,8),P('Jurisdiction, employer coverage and effective law must be rechecked with qualified HR/legal counsel before real use. The project contains no real applicant, medical, background-check, immigration or protected-group personal information.','SmallX'),
 P('REPRODUCE THIS CASE','SubheadX'),
 P('<font name="Corp-Bold">PYTHONPATH=src python -m tahr.cli demo</font>   |   <font name="Corp-Bold">PYTHONPATH=src python -m unittest discover -s tests -v</font>','SmallX')])

doc.build(story,onFirstPage=header_footer,onLaterPages=header_footer)
print('Built:',OUT,OUT.stat().st_size)
