import os
from dotenv import load_dotenv
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Load API key securely
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found. Make sure your .env file is configured.")

client = OpenAI(api_key=api_key)

def get_embedding(text, model="text-embedding-ada-002"):
    response = client.embeddings.create(
        input=[text],
        model=model
    )
    return response.data[0].embedding

def compute_similarity(job_text, resumes):
    job_emb = get_embedding(job_text)
    results = []

    for resume_id, resume_text in resumes.items():
        resume_emb = get_embedding(resume_text)
        score = cosine_similarity([job_emb], [resume_emb])[0][0]
        results.append((resume_id, score))

    results.sort(key=lambda x: x[1], reverse=True)
    return results[:10]  # Limit to top 10

def generate_summary(job_text, resume_text):
    prompt = f"""
You're a hiring assistant. Given a job description and a candidate's resume, write a brief, enthusiastic summary explaining why this person is a strong match for the role.

Be specific about:
- Relevant technical skills or experiences
- Impactful projects or roles
- Alignment with the job's responsibilities

Use 2-3 short paragraphs only. Be concise and persuasive.

Job Description:
{job_text}

Candidate Resume:
{resume_text[:1500]}

Summary:
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
