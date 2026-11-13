"""Portable zero-dependency dashboard: no CDN, API key or data exfiltration."""
from __future__ import annotations
import html
import json
from pathlib import Path
from .generate_data import ROOT


HTML = '''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Northstar simulated Talent Acquisition & HR operations scorecard">
<title>Northstar | Talent & People Operations</title>
<style>
:root{color-scheme:light;--navy:#10283f;--navy2:#173a53;--teal:#137b87;--ink:#163045;--muted:#52697a;--bg:#eff4f7;--white:#fff;--line:#dce6ec;--amber:#c08727;--pink:#aa4954}
*{box-sizing:border-box}body{margin:0;font:15px/1.5 system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:var(--bg);color:var(--ink)}
a{color:#116b77}.shell{max-width:1300px;margin:auto;padding:0 28px}header{background:linear-gradient(125deg,var(--navy),#19556c);color:white;padding:39px 0 36px}header .eyebrow{color:#80d5dd;font-size:12px;letter-spacing:.16em;text-transform:uppercase;font-weight:800}header h1{font-size:clamp(28px,4vw,47px);line-height:1.14;letter-spacing:-.035em;margin:10px 0 12px;font-weight:750}header p{color:#d3e4ed;max-width:900px;margin:0}header .stamp{margin-top:20px;display:inline-block;border:1px solid #7c9aab;border-radius:6px;padding:7px 11px;font-size:12px;letter-spacing:.05em}
main{padding:30px 0 60px}.toolbar{display:flex;justify-content:space-between;gap:15px;flex-wrap:wrap;align-items:center;margin-bottom:22px}.section-title{font-weight:760;font-size:23px;letter-spacing:-.025em;margin:30px 0 16px}.small{color:var(--muted);font-size:13px}.toolbar label{font-size:13px;font-weight:700}.toolbar select{padding:10px 14px;border:1px solid #aabdc8;border-radius:8px;background:white;color:var(--ink);font-size:14px;margin-left:8px}.cards{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}.card{background:white;border:1px solid var(--line);border-radius:11px;padding:19px;box-shadow:0 3px 14px #0d304708}.card .label{color:var(--muted);font-size:13px;font-weight:650}.card .value{font-size:33px;font-weight:780;letter-spacing:-.055em;margin-top:7px}.card .sub{font-size:12px;color:var(--muted);margin-top:5px}.columns{display:grid;grid-template-columns:1.15fr .85fr;gap:16px}.panel{background:white;border:1px solid var(--line);border-radius:11px;padding:22px;box-shadow:0 3px 14px #0d304708}.panel h3{margin:0 0 6px;font-size:18px}.panel p{color:var(--muted);font-size:13px;margin:0 0 20px}.funnelrow{display:grid;grid-template-columns:95px 1fr 82px;align-items:center;gap:11px;margin:13px 0}.barbg{height:14px;border-radius:5px;background:#e5eff2;overflow:hidden}.bar{height:100%;border-radius:5px;background:linear-gradient(90deg,#0c7989,#35a5ab)}.count{text-align:right;font-variant-numeric:tabular-nums;font-weight:700}.monthrow{display:flex;align-items:end;gap:8px;height:230px;border-bottom:1px solid #bfcdd6;padding-top:8px}.month{flex:1;text-align:center;min-width:0}.month .tall{height:170px;display:flex;align-items:end;justify-content:center}.month .monthbar{background:#237f91;min-width:15px;max-width:40px;width:75%;border-radius:4px 4px 0 0}.month .m{font-size:11px;color:var(--muted);white-space:nowrap;margin-top:6px}.month .n{font-weight:700;font-size:12px}table{width:100%;border-collapse:collapse}th{text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:#516b7d;background:#eef4f7}td,th{padding:11px 10px;border-bottom:1px solid #edf1f4}td{text-align:left;font-size:13px}td.num{text-align:right;font-variant-numeric:tabular-nums}th.num{text-align:right}.tablewrap{overflow-x:auto}.warning{border-left:4px solid var(--amber);padding:12px 16px;background:#fff8e9;margin-top:20px;border-radius:4px;font-size:13px}.endnote{font-size:12px;color:var(--muted);margin-top:20px}.footer{padding:20px 0;border-top:1px solid var(--line);color:var(--muted);font-size:12px}@media(max-width:1050px){.cards{grid-template-columns:repeat(2,minmax(0,1fr))}.columns{grid-template-columns:1fr}}@media(max-width:550px){.shell{padding:0 14px}.cards{grid-template-columns:1fr}.toolbar select{display:block;margin:6px 0 0;width:100%}.funnelrow{grid-template-columns:79px 1fr 57px}.panel{padding:16px}header{padding:28px 0}}@media print{header{background:white;color:var(--navy)}header p{color:var(--navy)}.card,.panel{break-inside:avoid}.toolbar{display:none}body{background:white}}
:focus-visible{outline:3px solid #bd7415;outline-offset:3px}
</style></head><body>
<header><div class="shell"><div class="eyebrow">People Analytics / Executive Operations</div><h1>Hiring that scales.<br>People operations that deliver.</h1><p>Fictional Northstar People & Talent | An end-to-end demonstration of recruiting throughput, hiring quality guardrails, onboarding and employee service delivery.</p><div class="stamp">SYNTHETIC DATA ONLY &nbsp;•&nbsp; SNAPSHOT: <span id="snapshot"></span></div></div></header>
<main class="shell">
<div class="toolbar"><div><strong>Executive scorecard</strong><div class="small">Descriptive measures; all results are part of a simulated scenario.</div></div><label for="department">Department <select id="department"><option value="All">All departments</option></select></label></div>
<div id="cards" class="cards" aria-live="polite"></div>
<h2 class="section-title">Recruiting performance</h2>
<div class="columns"><section class="panel"><h3>Stage reach / recruiting funnel</h3><p>Distinct applications that reached each stage; stages are not mutually exclusive.</p><div id="funnel"></div></section><section class="panel"><h3>Monthly hires</h3><p>Recorded hire-stage events per month.</p><div id="months"></div></section></div>
<h2 class="section-title">Talent acquisition and HR delivery</h2>
<div class="columns"><section class="panel"><h3>Talent source mix</h3><p>Hiring counts and raw hire conversion; open requisitions cause cohort immaturity.</p><div class="tablewrap"><table><thead><tr><th>Channel</th><th class="num">Applicants</th><th class="num">Hires</th><th class="num">Hire %</th></tr></thead><tbody id="sources"></tbody></table></div></section><section class="panel"><h3>People Operations service</h3><p>Ticket resolution and onboarding completion against fictional internal service targets.</p><div id="people-cards" class="cards" style="grid-template-columns:repeat(2,minmax(0,1fr))"></div><h3 style="margin-top:20px">Case categories</h3><div class="tablewrap"><table><thead><tr><th>Type</th><th class="num">Total</th><th class="num">Open</th></tr></thead><tbody id="hrcases"></tbody></table></div></section></div>
<div class="warning"><strong>Decision guardrails:</strong> This dashboard never grades, ranks, profiles or recommends applicants. Voluntary demographic audit data are in a restricted, separate file; public dashboards only use non-sensitive aggregates. Rates are descriptive and should not be interpreted as causal effects, compliance determinations or real employer outcomes.</div>
<div class="endnote" id="notes"></div>
</main><footer class="footer"><div class="shell">Northstar People & Talent (fictional) • Static offline dashboard • Rebuild from source using <code>python -m tahr.cli demo</code> • No analytics trackers or third-party network calls.</div></footer>
<script id="payload" type="application/json">__DATA__</script>
<script>
'use strict';
const data=JSON.parse(document.getElementById('payload').textContent),r=data.recruiting,p=data.people_operations;
const number=v=>v===null||v===undefined?'—':Number(v).toLocaleString('en-US');
const percent=v=>v===null||v===undefined?'—':(Number(v).toFixed(1)+'%');
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const card=(l,v,s)=>`<div class="card"><div class="label">${esc(l)}</div><div class="value">${esc(v)}</div><div class="sub">${esc(s)}</div></div>`;
document.getElementById('snapshot').textContent=data.metadata.as_of;
const depts=r.requisitions.by_department;
for(const d of depts){const e=document.createElement('option');e.value=d.department;e.textContent=d.department;document.getElementById('department').append(e)}
function renderCards(){const name=document.getElementById('department').value;const d=depts.find(x=>x.department===name);const open=d?d.open:r.requisitions.by_status.Open,filled=d?d.filled:r.requisitions.by_status.Filled;const total=d?d.total:r.requisitions.total;
 document.getElementById('cards').innerHTML=card('Requisitions',number(total),'Open + filled + cancelled')+card('Open requisitions',number(open),'Approved headcount demand')+card('Filled requisitions',number(filled),'Completed placements')+card('Candidates / applications',name==='All'?number(r.applications):'All teams','Application-level funnel below is company-wide')+card('Average time to fill',name==='All'?number(r.time_to_fill_days.mean)+' d':'Company-wide',`Target ${r.time_to_fill_days.target_days} days; filled roles only`)+card('Time to hire',number(r.time_to_hire_days.mean)+' d',`Target ${r.time_to_hire_days.target_days} days; hires only`)+card('Offer acceptance',percent(r.offers.acceptance_pct),`${r.offers.accepted}/${r.offers.decided} decided offers; ${r.offers.pending} pending`)+card('Candidate survey favorable',percent(r.candidate_experience.favorable_pct),`${r.candidate_experience.survey_responses} voluntary responses; nonresponse bias`);
}
document.getElementById('department').addEventListener('change',renderCards);renderCards();
const max=Math.max(...r.funnel.map(x=>x.reached));
document.getElementById('funnel').innerHTML=r.funnel.map(x=>`<div class="funnelrow"><strong>${esc(x.stage)}</strong><div class="barbg" role="img" aria-label="${esc(x.stage)} ${x.reached} applications"><div class="bar" style="width:${Math.max(0,100*x.reached/max).toFixed(2)}%"></div></div><span class="count">${number(x.reached)}</span></div>`).join('');
const mmax=Math.max(...r.monthly_hires.map(x=>x.hired));
document.getElementById('months').innerHTML='<div class="monthrow">'+r.monthly_hires.map(x=>`<div class="month"><div class="n">${x.hired}</div><div class="tall"><div class="monthbar" role="img" aria-label="${esc(x.month)}: ${x.hired} hires" style="height:${Math.max(4,x.hired/mmax*165)}px"></div></div><div class="m">${esc(x.month.slice(5))}</div></div>`).join('')+'</div><div class="small" style="margin-top:12px">Month labels are 2026 (MM).</div>';
document.getElementById('sources').innerHTML=r.source_performance.map(x=>`<tr><td>${esc(x.source)}</td><td class="num">${number(x.applicants)}</td><td class="num">${number(x.hires)}</td><td class="num">${percent(x.hire_conversion_pct)}</td></tr>`).join('');
document.getElementById('people-cards').innerHTML=card('Active workforce',number(p.headcount.active),'Synthetic HRIS snapshot')+card('HR tickets open',number(p.hr_service_cases.open),`${p.hr_service_cases.overdue_open} overdue against ${p.hr_service_cases.sla_days} calendar-day SLA`)+card('HR resolved in SLA',percent(p.hr_service_cases.sla_pct_of_resolved),'Of resolved tickets only')+card('Onboarding on time',percent(p.onboarding.on_time_pct_of_due),`Of ${p.onboarding.due_by_snapshot} tasks due by snapshot`);
document.getElementById('hrcases').innerHTML=p.hr_service_cases.by_category.map(x=>`<tr><td>${esc(x.category)}</td><td class="num">${x.total}</td><td class="num">${x.open}</td></tr>`).join('');
document.getElementById('notes').textContent='Definitions: stage reach is ever-attained; accepted / (accepted + declined) excludes pending offers; time-to-fill = filled requisition close minus open; onboarding on-time = all tasks completed by their due date / all tasks due by snapshot. See docs/technical/metric_dictionary.md for full definitions.';
</script></body></html>'''


def write_html(root: Path = ROOT) -> Path:
    metrics = json.loads((root / "reports/metrics.json").read_text())
    text = json.dumps(metrics, ensure_ascii=True).replace("<", "\\u003c")
    target = root / "reports/dashboard.html"
    target.write_text(HTML.replace("__DATA__", text), encoding="utf-8")
    return target
