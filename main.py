import streamlit as st
from recommender import compute_similarity, generate_summary
from resume_parser import extract_text_from_pdf, extract_text_from_docx
from dotenv import load_dotenv
import os

load_dotenv()
st.set_page_config(page_title="Candidate Recommender", layout="wide")

# 🎨 Custom CSS for cleaner dashboard UI
st.markdown("""
    <style>
        body {
            background-color: #0f172a;
            color: #f1f5f9;
        }
        .candidate-card {
            background-color: #1e293b;
            border-radius: 10px;
            padding: 1rem 1.5rem;
            margin-bottom: 1.2rem;
            max-width: 1000px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        .score-badge {
            font-weight: 600;
            font-size: 1.85rem;
            border-radius: 9999px;
            padding: 0.3rem 0.8rem;
            display: inline-block;
        }
        .perfect { background-color: #22c55e; color: #fff; }
        .strong { background-color: #facc15; color: #1e293b; }
        .decent { background-color: #fb923c; color: #1e293b; }
        .weak { background-color: #ef4444; color: #fff; }
        .summary-box {
            background-color: #0f172a;
            border: 1px solid #334155;
            padding: 1rem;
            margin-top: 1rem;
            border-radius: 8px;
            font-size: 1.0rem;
            line-height: 1.6;
            max-width: 900px;
        }
        .highlight {
            font-size: 1.1rem;
            font-weight: 600;
        }
        code {
            background-color: #1e293b;
            padding: 0.2rem 0.5rem;
            border-radius: 5px;
        }
        .header {
            font-size: 2.2rem;
            margin-bottom: 1.2rem;
            font-weight: 700;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='header'>🧠 Candidate Recommendation Engine</div>", unsafe_allow_html=True)
st.caption("Find the most relevant candidates for your job using OpenAI embeddings and smart summaries.")

job_desc = st.text_area("📄 Paste the job description", height=260)

uploaded_files = st.file_uploader(
    "📥 Upload candidate resumes (PDF or DOCX)",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

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
        st.info("🔍 Processing resumes...")

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

            st.markdown(f"""
            <div class="candidate-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>👤 <span class="highlight">{idx}. {candidate_name}</span></div>
                    <div>🎯 Score: <code>{score:.3f}</code> {get_score_label(score)}</div>
                </div>
                <div class="summary-box">
                    <strong>💬 Why is this person a good fit?</strong><br><br>
                    ⏳ Generating summary...
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.spinner("Calling GPT..."):
                summary = generate_summary(job_desc, resumes[filename])
                st.markdown(f"""<div class="summary-box">{summary}</div>""", unsafe_allow_html=True)

