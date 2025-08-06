import os
from dotenv import load_dotenv
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# ✅ Make sure .env is loaded BEFORE accessing the key
load_dotenv()

# ✅ Safely load the key from environment
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found. Make sure .env file exists and contains the API key.")

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
    return results[:10]

def generate_summary(job_text, resume_text):
    prompt = f"""Compare the job description and resume below. Explain why this person is a good fit.

Job Description:
{job_text}

Candidate Resume:
{resume_text[:1500]}

Summary:"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
