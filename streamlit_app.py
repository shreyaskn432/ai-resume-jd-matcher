import streamlit as st
import PyPDF2
import matplotlib.pyplot as plt
import json

from app.llm_client import generate_match_report
from app.parser import parse_match_report
from app.scorer import interpret_score
from app.skill_matcher import analyze_skills

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")

st.title("🚀 AI Resume Analyzer")

# -------- SIDEBAR --------
st.sidebar.header("Upload Resume")

uploaded_file = st.sidebar.file_uploader("Upload Resume (PDF/TXT)", type=["pdf", "txt"])

resume_text = ""

if uploaded_file:
    if uploaded_file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            if page.extract_text():
                resume_text += page.extract_text()
    else:
        resume_text = uploaded_file.read().decode("utf-8")

# -------- MAIN INPUT --------
st.subheader("📄 Job Description")
jd = st.text_area("Paste Job Description")

# -------- ANALYZE BUTTON --------
if st.button("🔍 Analyze Resume"):

    if resume_text and jd:
        with st.spinner("Analyzing with AI..."):

            # AI Output
            raw_output = generate_match_report(resume_text, jd)

            # Parse
            report = parse_match_report(raw_output)

            # Score label
            fit_label = interpret_score(report.match_score)

            # Skill matching
            skill_data = analyze_skills(resume_text, jd)

        st.success("Analysis Complete ✅")

        # -------- METRICS --------
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Match Score", f"{report.match_score}%")
            st.progress(report.match_score / 100)

        with col2:
            st.metric("Skill Match", f"{skill_data['match_percent']}%")
            st.progress(skill_data['match_percent'] / 100)

        with col3:
            st.metric("Fit Level", fit_label)

        # -------- CHART --------
        st.subheader("📊 Score Visualization")

        fig, ax = plt.subplots()
        ax.bar(["Match Score", "Skill Match"], 
               [report.match_score, skill_data['match_percent']])
        ax.set_ylim(0, 100)
        st.pyplot(fig)

        # -------- DETAILS --------
        col4, col5 = st.columns(2)

        with col4:
            st.subheader("✅ Strengths")
            for s in report.strengths:
                st.write(f"✔ {s}")

            st.subheader("❌ Weaknesses")
            for w in report.weaknesses:
                st.write(f"❌ {w}")

        with col5:
            st.subheader("💡 Suggestions")
            for s in report.suggestions:
                st.write(f"💡 {s}")

            st.subheader("🧠 Missing Skills")
            for skill in skill_data["missing_skills"]:
                st.write(f"❌ {skill}")

        # -------- DOWNLOAD --------
        result = {
            "match_score": report.match_score,
            "skill_match": skill_data['match_percent'],
            "fit_label": fit_label,
            "strengths": report.strengths,
            "weaknesses": report.weaknesses,
            "missing_skills": skill_data["missing_skills"],
            "suggestions": report.suggestions
        }

        st.download_button(
            "📥 Download Report",
            json.dumps(result, indent=2),
            "report.json"
        )

    else:
        st.warning("Please upload resume and enter job description")