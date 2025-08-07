import streamlit as st
from recommender import compute_similarity, generate_summary
from resume_parser import extract_text_from_pdf, extract_text_from_docx
from dotenv import load_dotenv
import os

load_dotenv()
st.set_page_config(page_title="Candidate Recommender", layout="wide")

# Theme toggle (light/dark)
theme = st.sidebar.radio("Select Theme", ("Light", "Dark"))

if theme == "Dark":
    background = "#0f172a"
    card = "#1e293b"
    text = "#f1f5f9"
else:
    background = "#ffffff"
    card = "#f8fafc"
    text = "#1e293b"

st.markdown(f"""
    <style>
        body {{ background-color: {background}; color: {text}; }}
        .candidate-card {{
            background-color: {card};
            border-radius: 10px;
            padding: 1rem 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .score-badge {{
            font-weight: 600;
            font-size: 0.85rem;
            border-radius: 9999px;
            padding: 0.3rem 0.8rem;
            display: inline-block;
        }}
        .perfect {{ background-color: #22c55e; color: white; }}
        .strong {{ background-color: #facc15; color: #1e293b; }}
        .decent {{ background-color: #fb923c; color: white; }}
        .weak {{ background-color: #ef4444; color: white; }}
        .summary-box {{
            font-size: 1.62rem;
            line-height: 1.6;
            padding: 0.8rem 0;
        }}
        .resume-links {{
            margin-top: 0.5rem;
            font-size: 0.9rem;
        }}
    </style>
""", unsafe_allow_html=True)

st.title("🧠 Candidate Recommendation Engine")
st.caption("Find top matching candidates and explore smart summaries using OpenAI embeddings.")

job_desc = st.text_area("📄 Paste the job description", height=460)

uploaded_files = st.file_uploader(
    "📥 Upload candidate resumes (PDF or DOCX)",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

if uploaded_files:
    st.markdown(f"### 📂 {len(uploaded_files)} Resumes Uploaded")

def get_score_label(score):
    if score >= 0.85:
        return '<span class="score-badge perfect">Perfect Match</span>'
    elif score >= 0.75:
        return '<span class="score-badge strong">Strong Fit</span>'
    elif score >= 0.65:
        return '<span class="score-badge decent">Decent Fit</span>'
    else:
        return '<span class="score-badge weak">Weak Fit</span>'

if st.button("🚀 Find Best Matches"):
    if not job_desc or not uploaded_files:
        st.warning("Please provide both a job description and at least one resume.")
    else:
        resumes = {}
        for file in uploaded_files:
            if file.name.endswith(".pdf"):
                text = extract_text_from_pdf(file)
            elif file.name.endswith(".docx"):
                text = extract_text_from_docx(file)
            resumes[file.name] = text

        results = compute_similarity(job_desc, resumes)
        results = results[:10]

        st.markdown("## ✅ Top Matching Candidates")

        for idx, (filename, score) in enumerate(results, start=1):
            candidate_name = filename.replace(".pdf", "").replace(".docx", "").replace("-", " ")
            label = get_score_label(score)

            st.markdown(f"""
                <div class='candidate-card'>
                    <div style='display:flex; justify-content:space-between;'>
                        <div><strong>👤 {idx}. {candidate_name}</strong></div>
                        <div>🎯 Score: <code>{score:.3f}</code> {label}</div>
                    </div>
                    <div class='resume-links'>
                        📎 <a href='#' onclick="return false">View Resume</a> | <a href='#' onclick="return false">Download</a>
                    </div>
            """, unsafe_allow_html=True)

            with st.expander("📘 Summary of Fit"):
                with st.spinner("Generating summary..."):
                    summary = generate_summary(job_desc, resumes[filename])
                    st.markdown(f"<div class='summary-box'>{summary}</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)
