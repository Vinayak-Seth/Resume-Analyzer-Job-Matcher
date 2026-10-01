"""Streamlit UI for the Resume Analyzer & Job Matcher."""
import json

import streamlit as st

from src.analyzer import Analyzer
from src.config import get_api_key, load_config
from src.parser import read_resume

ICONS = {"match": "✅", "partial": "🟡", "missing": "❌"}

st.set_page_config(page_title="Resume Analyzer & Job Matcher", page_icon="📄", layout="wide")


@st.cache_resource
def get_analyzer() -> Analyzer:
    return Analyzer(load_config(), get_api_key())


st.title("📄 Resume Analyzer & Job Matcher")
st.caption("LLM-powered entity extraction + semantic resume-to-job matching")

try:
    analyzer = get_analyzer()
except Exception as e:
    st.error(str(e))
    st.stop()

min_chars = analyzer.cfg["input"]["min_resume_chars"]
left, right = st.columns(2)

with left:
    st.subheader("Resume")
    upload = st.file_uploader("Upload PDF or TXT", type=["pdf", "txt"])
    pasted = st.text_area("...or paste resume text", height=200)
with right:
    st.subheader("Job description")
    job_text = st.text_area("Paste the job description", height=330)

if st.button("Analyze", type="primary"):
    resume_text = read_resume(upload) if upload else pasted.strip()
    if len(resume_text) < min_chars:
        st.warning("Resume text is too short or unreadable (scanned PDF?). Paste the text instead.")
        st.stop()
    if not job_text.strip():
        st.warning("Please paste a job description.")
        st.stop()
    try:
        with st.spinner("Extracting entities and matching..."):
            st.session_state["result"] = analyzer.analyze(resume_text, job_text)
    except Exception as e:
        st.error(f"Analysis failed: {e}")
        st.stop()

res = st.session_state.get("result")
if res:
    m, resume, job = res["match"], res["resume"], res["job"]
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Match score (LLM)", f"{m.overall_score}/100")
    c2.metric("Verdict", res["verdict"])
    c3.metric("Keyword-only baseline", f"{res['baseline']}%",
              help="% of must-have skills literally found in the resume")
    st.info(m.summary)

    t1, t2, t3, t4 = st.tabs(["Skill match", "Gaps & advice", "Extracted resume", "Extracted job"])
    with t1:
        for s in m.skill_matches:
            flag = "" if res["evidence_ok"].get(s.requirement, True) else " ⚠️ quote not found in resume"
            st.markdown(f"{ICONS[s.status]} **{s.requirement}** ({s.status}){flag}")
            if s.evidence:
                st.caption(f"“{s.evidence}”")
    with t2:
        a, b = st.columns(2)
        a.markdown("**Strengths**\n" + "\n".join(f"- {x}" for x in m.strengths))
        a.markdown("**Transferable skills**\n" + "\n".join(f"- {x}" for x in m.transferable_skills))
        b.markdown("**Missing requirements**\n" + "\n".join(f"- {x}" for x in m.missing_requirements))
        b.markdown("**Improve your resume**\n" + "\n".join(f"- {x}" for x in m.improvement_suggestions))
    with t3:
        st.json(resume.model_dump())
    with t4:
        st.json(job.model_dump())

    report = {k: res[k].model_dump() for k in ("resume", "job", "match")}
    report.update(verdict=res["verdict"], keyword_baseline=res["baseline"])
    st.download_button("Download report (JSON)", json.dumps(report, indent=2),
                       "report.json", "application/json")
