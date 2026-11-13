"""Optional SQL-backed Streamlit view (pip install -r requirements-dashboard.txt)."""
from __future__ import annotations
import sqlite3
from contextlib import closing
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from tahr.metrics import calculate
import json

st.set_page_config(page_title="Northstar | Talent & HR", page_icon="📊", layout="wide")
st.title("Talent acquisition & People Operations")
st.caption("Northstar People & Talent - FICTIONAL SYNTHETIC SNAPSHOT - analytics only; not candidate selection")
db = ROOT / "data/processed/talent_hr.sqlite"
if not db.exists():
    st.error("Run PYTHONPATH=src python -m tahr.cli demo from the repository root before launching the app.")
    st.stop()

@st.cache_data

def load():
    with closing(sqlite3.connect(f"file:{db}?mode=ro", uri=True)) as conn:
        req = pd.read_sql_query("SELECT req_id,department,status,opened_at,closed_at FROM requisitions", conn)
        src = pd.read_sql_query("""SELECT r.department,a.source,a.current_stage,
            a.application_id FROM applications a JOIN requisitions r ON a.req_id=r.req_id""", conn)
        hr = pd.read_sql_query("SELECT category,status FROM hr_cases", conn)
        funnel = pd.read_sql_query("""SELECT r.department,e.stage,COUNT(DISTINCT e.application_id) n
           FROM stage_events e JOIN applications a ON e.application_id=a.application_id
           JOIN requisitions r ON r.req_id=a.req_id GROUP BY r.department,e.stage""", conn)
    return req,src,hr,funnel

req, src,hr,funnel = load()
sel = st.selectbox("Department", ["All"] + sorted(req.department.unique().tolist()))
if sel != "All":
    req=req[req.department==sel]
    src=src[src.department==sel]
    funnel=funnel[funnel.department==sel]
cols=st.columns(4)
cols[0].metric("Requisitions",len(req))
cols[1].metric("Currently open",(req.status=="Open").sum())
cols[2].metric("Filled",(req.status=="Filled").sum())
cols[3].metric("Applications",len(src))
st.markdown("### Pipeline attainment")
order={name:i for i,name in enumerate(["Applied","Screened","Interview","Final","Offer","Hired"])}
agg=funnel.groupby("stage",as_index=False)["n"].sum()
agg["ord"]=agg.stage.map(order)
fig=px.bar(agg.sort_values("ord"),x="stage",y="n",color_discrete_sequence=["#147b88"],labels={"n":"Candidates reaching stage", "stage":"Stage"})
st.plotly_chart(fig,use_container_width=True)
left,right=st.columns(2)
with left:
    st.markdown("### Hiring source counts")
    by_src=src.assign(hired=src.current_stage.eq("Hired")).groupby("source",as_index=False).agg(applicants=("application_id","count"),hires=("hired","sum"))
    st.dataframe(by_src.sort_values("hires",ascending=False),use_container_width=True,hide_index=True)
with right:
    st.markdown("### HR ticket volume (all departments)")
    st.plotly_chart(px.bar(hr.groupby(["category","status"]).size().reset_index(name="n"),
        x="category",y="n",color="status",barmode="stack"),use_container_width=True)
st.info("All records are synthesized. Department filter does not filter company-wide HR tickets. Do not use this app to make hiring decisions; sensitive audit group file is deliberately excluded.")
