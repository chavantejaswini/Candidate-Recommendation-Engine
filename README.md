# Candidate-Recommendation-Engine

## Overview
This is a simple web app to recommend top candidates for a job based on their resumes using cosine similarity over embeddings.

## Features
- Accepts job description and multiple resumes
- Uses OpenAI Embeddings
- Ranks candidates by relevance
- Optional: AI-generated summary of fit

## Tech Stack
- Python, Streamlit
- OpenAI embeddings
- PyPDF2, python-docx

## How to Run
```bash
pip install -r requirements.txt
streamlit run main.py

