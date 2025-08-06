import streamlit as st
from recommender import compute_similarity, generate_summary
from resume_parser import extract_text_from_pdf, extract_text_from_docx
from dotenv import load_dotenv
import os

load_dotenv()  # Load from .env if exists

st.set_page_config(page_title="Candidate Recommender", layout="wide")
st.title("📄 Candidate Recommendation Engine")

st.markdown("Upload resumes and a job description to find the best candidates using OpenAI embeddings.")

job_desc = st.text_area("📌 Paste the job description here", height=200)

uploaded_files = st.file_uploader(
    "📤 Upload candidate resumes (PDF or DOCX)",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

def get_match_label(score):
    if score >= 0.85:
        return "🟢 Perfect Match"
    elif score >= 0.75:
        return "🟡 Strong Fit"
    elif score >= 0.65:
        return "🟠 Decent Fit"
    else:
        return "🔴 Weak Fit"

if st.button("🔍 Find Best Matches"):
    if not job_desc or not uploaded_files:
        st.warning("Please provide both a job description and at least one resume.")
    else:
        st.info("⏳ Processing resumes. Please wait...")

        resumes = {}

        for file in uploaded_files:
            if file.name.endswith(".pdf"):
                text = extract_text_from_pdf(file)
            elif file.name.endswith(".docx"):
                text = extract_text_from_docx(file)
            resumes[file.name] = text

        results = compute_similarity(job_desc, resumes)
        results = results[:10]  # 🔥 Limit to top 10 as required

        st.subheader("✅ Top Matching Candidates")
        for i, (name, score) in enumerate(results, start=1):
            label = get_match_label(score)
            st.markdown(f"### {i}. **{name}** — Similarity Score: `{score:.3f}` {label}")

            with st.expander("💬 Why is this person a good fit?"):
                st.markdown("⏳ Generating summary...")
                summary = generate_summary(job_desc, resumes[name])
                st.write(summary)
