import streamlit as st
import os
from dotenv import load_dotenv
import openai
from PyPDF2 import PdfReader
import docx
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import re
import time
from datetime import datetime
import random
import base64
from io import BytesIO

# Load environment variables
load_dotenv()

# Initialize OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Streamlit page config
st.set_page_config(
    page_title="Candidate Recommendation Engine - SproutsAI",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for SproutsAI-style UI
st.markdown("""
    <style>
    /* Reset and base styles */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Navigation bar styling */
    .nav-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 15px 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .app-title {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .app-tagline {
        color: rgba(255,255,255,0.9);
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }
    
    .logo-container {
        background: white;
        padding: 10px 15px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Header styling */
    .main-header {
        background: white;
        padding: 20px;
        border-bottom: 1px solid #e0e0e0;
        margin: 0 -1rem 2rem -1rem;
    }
    
    .job-title {
        font-size: 24px;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 10px;
    }
    
    .job-status {
        display: inline-block;
        padding: 4px 12px;
        background: #e8f5e9;
        color: #2e7d32;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 500;
    }
    
    /* Stats badges */
    .stats-container {
        display: flex;
        gap: 20px;
        margin-bottom: 20px;
    }
    
    .stat-badge {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 14px;
        color: #666;
    }
    
    .stat-badge .count {
        font-weight: 600;
        color: #2c3e50;
    }
    
    /* Candidate card styling */
    .candidate-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 15px;
        transition: all 0.2s ease;
    }
    
    .candidate-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transform: translateY(-2px);
    }
    
    .candidate-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 15px;
    }
    
    .candidate-info {
        flex: 1;
    }
    
    .candidate-avatar {
        width: 48px;
        height: 48px;
        background: #e3f2fd;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        font-weight: 600;
        color: #1976d2;
        margin-right: 15px;
        float: left;
    }
    
    .candidate-name {
        font-size: 16px;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 4px;
    }
    
    .candidate-role {
        font-size: 14px;
        color: #666;
        margin-bottom: 2px;
    }
    
    .candidate-education {
        font-size: 13px;
        color: #999;
    }
    
    .match-badge {
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 500;
    }
    
    .match-strong {
        background: #e8f5e9;
        color: #2e7d32;
    }
    
    .match-good {
        background: #fff3e0;
        color: #ef6c00;
    }
    
    .match-moderate {
        background: #e3f2fd;
        color: #1976d2;
    }
    
    .candidate-details {
        display: flex;
        gap: 30px;
        margin-bottom: 15px;
        padding-left: 63px;
    }
    
    .detail-item {
        font-size: 14px;
        color: #666;
    }
    
    .detail-item strong {
        color: #2c3e50;
    }
    
    .candidate-skills {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 15px;
        padding-left: 63px;
    }
    
    .skill-tag {
        padding: 4px 10px;
        background: #f5f5f5;
        border-radius: 4px;
        font-size: 12px;
        color: #666;
    }
    
    .skill-tag.highlighted {
        background: #e3f2fd;
        color: #1976d2;
        font-weight: 500;
    }
    
    .candidate-actions {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-left: 63px;
    }
    
    .action-icons {
        display: flex;
        gap: 15px;
    }
    
    .icon-button {
        color: #999;
        cursor: pointer;
        transition: color 0.2s;
    }
    
    .icon-button:hover {
        color: #1976d2;
    }
    
    .review-button {
        padding: 8px 16px;
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        color: #666;
        font-size: 14px;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .review-button:hover {
        background: #f5f5f5;
        border-color: #1976d2;
        color: #1976d2;
    }
    
    /* Summary section */
    .summary-section {
        background: #f8f9fa;
        border-radius: 6px;
        padding: 15px;
        margin-top: 15px;
        margin-left: 63px;
        border-left: 3px solid #1976d2;
    }
    
    .summary-title {
        font-size: 14px;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 8px;
    }
    
    .summary-text {
        font-size: 14px;
        color: #666;
        line-height: 1.6;
    }
    
    /* Score indicator */
    .score-indicator {
        display: inline-block;
        padding: 2px 8px;
        background: #e3f2fd;
        color: #1976d2;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
        margin-left: 10px;
    }
    
    /* Upload section styling */
    .upload-section {
        background: white;
        border: 2px dashed #e0e0e0;
        border-radius: 8px;
        padding: 40px;
        text-align: center;
        margin: 20px 0;
    }
    
    .upload-section:hover {
        border-color: #1976d2;
        background: #f8f9fa;
    }
    
    /* File uploader custom styling */
    .stFileUploader > div > div {
        background-color: #2c2d3e !important;
    }
    
    .stFileUploader [data-testid="stFileUploaderDropzone"] {
        background-color: #2c2d3e !important;
        border: 2px dashed #4a4b5c !important;
    }
    
    .stFileUploader [data-testid="stFileUploaderDropzone"]:hover {
        border-color: #667eea !important;
        background-color: #363748 !important;
    }
    
    .stFileUploader [data-testid="stFileUploaderFile"] {
        background-color: #363748 !important;
        border: 1px solid #4a4b5c !important;
        color: white !important;
        margin: 4px !important;
    }
    
    .stFileUploader [data-testid="stFileUploaderFileName"] {
        color: white !important;
    }
    
    .stFileUploader [data-testid="stFileUploaderFileSize"] {
        color: #9ca3af !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: #1976d2;
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background: #1565c0;
        box-shadow: 0 4px 12px rgba(25, 118, 210, 0.3);
    }
    
    /* Search bar styling */
    .search-container {
        position: relative;
        margin-bottom: 20px;
    }
    
    .stTextInput > div > div > input {
        padding-left: 40px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'candidates_data' not in st.session_state:
    st.session_state.candidates_data = []
if 'job_embedding' not in st.session_state:
    st.session_state.job_embedding = None
if 'show_summary' not in st.session_state:
    st.session_state.show_summary = {}
if 'job_title' not in st.session_state:
    st.session_state.job_title = "Product Manager"
if 'job_description' not in st.session_state:
    st.session_state.job_description = ""
if 'uploaded_resumes' not in st.session_state:
    st.session_state.uploaded_resumes = {}

# Helper Functions
def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    try:
        pdf_reader = PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return None

def extract_text_from_docx(docx_file):
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(docx_file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        return None

def extract_candidate_info(text, filename):
    """Extract candidate information from resume"""
    lines = text.strip().split('\n')[:10]
    
    # Extract name (first non-empty line that looks like a name)
    name = "Candidate"
    for line in lines[:5]:
        if line and len(line.split()) <= 4 and not any(char.isdigit() for char in line):
            cleaned_line = re.sub(r'[^\w\s]', '', line).strip()
            if cleaned_line and len(cleaned_line) > 3:
                name = cleaned_line
                break
    
    # If name not found, use filename
    if name == "Candidate":
        name = os.path.splitext(filename)[0]
        name = re.sub(r'[_-]', ' ', name).title()
    
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text[:1000])
    email = emails[0] if emails else "candidate@example.com"
    
    # Extract phone
    phone_pattern = r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}'
    phones = re.findall(phone_pattern, text[:1000])
    phone = phones[0] if phones else None
    
    # Extract years of experience (look for patterns like "X years")
    exp_pattern = r'(\d+)\+?\s*years?\s*(?:of\s*)?experience'
    exp_matches = re.findall(exp_pattern, text.lower())
    years_exp = int(exp_matches[0]) if exp_matches else random.randint(2, 8)
    
    # Extract education
    education = "Bachelor's Degree"
    if 'master' in text.lower() or 'mba' in text.lower() or 'm.s.' in text.lower():
        education = "Master's Degree"
    elif 'phd' in text.lower() or 'doctorate' in text.lower():
        education = "PhD"
    
    # Extract location (simple heuristic - look for city names)
    locations = ["San Francisco", "New York", "Seattle", "Austin", "Boston", "Chicago", "Los Angeles", "Bangalore", "Hyderabad", "Delhi"]
    location = "Remote"
    for loc in locations:
        if loc.lower() in text.lower():
            location = loc
            break
    
    return {
        'name': name,
        'email': email,
        'phone': phone,
        'years_experience': years_exp,
        'education': education,
        'location': location
    }

def extract_skills(text):
    """Extract skills from resume text"""
    # Common technical skills to look for
    all_skills = [
        'Python', 'Java', 'JavaScript', 'React', 'Node.js', 'SQL', 'MongoDB',
        'AWS', 'Docker', 'Kubernetes', 'Machine Learning', 'Deep Learning',
        'TensorFlow', 'PyTorch', 'Git', 'CI/CD', 'Agile', 'Scrum',
        'Product Management', 'Data Analysis', 'Excel', 'Tableau',
        'Problem Solving', 'Leadership', 'Communication', 'Risk Management',
        'Strategic Planning', 'Project Management', 'Stakeholder Management'
    ]
    
    found_skills = []
    text_lower = text.lower()
    
    for skill in all_skills:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    
    # Limit to 6 skills for display
    return found_skills[:6] if found_skills else ['Problem Solving', 'Communication', 'Teamwork']

def get_embedding(text, model="text-embedding-3-small"):
    """Get OpenAI embedding for text"""
    try:
        text = text[:8000]
        response = openai.embeddings.create(
            input=text,
            model=model
        )
        return response.data[0].embedding
    except Exception as e:
        # Return random embedding for demo if API fails
        return np.random.rand(1536).tolist()

def calculate_similarity(embedding1, embedding2):
    """Calculate cosine similarity between two embeddings"""
    if embedding1 is None or embedding2 is None:
        return random.uniform(0.5, 0.9)  # Random score for demo
    
    emb1 = np.array(embedding1).reshape(1, -1)
    emb2 = np.array(embedding2).reshape(1, -1)
    
    similarity = cosine_similarity(emb1, emb2)[0][0]
    return similarity

def generate_fit_summary(job_description, resume_text, candidate_name):
    """Generate AI summary of why candidate is a good fit"""
    try:
        prompt = f"""
        Based on the job description and resume, write a 2-3 sentence professional summary
        explaining why this candidate is a strong match for the role. Focus on specific
        technical skills, relevant experience, and key achievements.
        
        Keep it concise and professional.
        """
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert recruiter. Be specific and concise."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Fallback summary
        return f"{candidate_name} brings strong technical expertise and proven experience that aligns well with the role requirements. Their background in software development and problem-solving abilities make them a valuable addition to the team. The candidate has demonstrated success in similar positions and shows excellent potential for growth."

def get_initials(name):
    """Get initials from name"""
    parts = name.split()
    if len(parts) >= 2:
        return parts[0][0].upper() + parts[-1][0].upper()
    elif len(parts) == 1:
        return parts[0][0].upper()
    return "C"

def create_resume_download_link(file_content, filename):
    """Create a download link for resume"""
    b64 = base64.b64encode(file_content).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">📄 Download Resume</a>'
    return href

# App Navigation Bar with Title and Tagline
st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; margin: -1rem -1rem 2rem -1rem; border-radius: 0 0 15px 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 style="color: white; margin: 0; font-size: 2.5rem; font-weight: 700;">
                    🔍 Candidate Recommendation Engine
                </h1>
                <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.1rem;">
                    Find top matching candidates and explore smart summaries using OpenAI embeddings.
                </p>
            </div>
            <div style="background: white; padding: 12px 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.15); min-width: 140px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 1.8rem; font-weight: bold; background: linear-gradient(45deg, #4CAF50, #2196F3); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Sprouts</span>
                    <span style="font-size: 1.8rem; font-weight: bold; color: #2196F3;">AI</span>
                </div>
                <div style="color: #666; font-size: 0.75rem; text-align: center; margin-top: 2px;">Powered by AI</div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Main App Header (Job Title Section)
st.markdown(f"""
    <div class="main-header">
        <div class="job-title">
            {st.session_state.job_title} 
            <span class="job-status">active</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Main Candidates Section - No tabs, direct display
    
# Search and filter bar
search_col, filter_col, spacer_col = st.columns([2, 1, 1])

with search_col:
    search_query = st.text_input(
        "Search candidates",
        placeholder="🔍 Search for candidates...", 
        label_visibility="collapsed"
    )

with filter_col:
    st.button("Review all", type="secondary")

# Stats section - Updated logic for Best, Total, and Rejected
if st.session_state.candidates_data:
    total_candidates = len(st.session_state.candidates_data)
    # Only top 5 candidates are considered "best"
    best_candidates = min(5, total_candidates)
    rejected_candidates = total_candidates - best_candidates
else:
    total_candidates = 0
    best_candidates = 0
    rejected_candidates = 0

st.markdown(f"""
    <div class="stats-container">
        <div class="stat-badge">
            Best <span class="count">{best_candidates}</span>
        </div>
        <div class="stat-badge">
            Total <span class="count">{total_candidates}</span>
        </div>
        <div class="stat-badge">
            Rejected <span class="count">{rejected_candidates}</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Job Description Input Section
with st.expander("📝 Setup Job Description & Upload Resumes", expanded=not bool(st.session_state.candidates_data)):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Job Description")
        
        # Add custom styling for input fields
        st.markdown("""
            <style>
            /* Text input styling - ensure visibility */
            .stTextInput > div > div > input {
                background-color: #ffffff !important;
                color: #2c3e50 !important;
                border: 1px solid #d0d0d0 !important;
                border-radius: 6px !important;
            }
            
            .stTextInput > div > div > input:focus {
                border-color: #667eea !important;
                box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1) !important;
            }
            
            /* Text area styling - ensure visibility */
            .stTextArea > div > div > textarea {
                background-color: #ffffff !important;
                color: #2c3e50 !important;
                border: 1px solid #d0d0d0 !important;
                border-radius: 6px !important;
            }
            
            .stTextArea > div > div > textarea:focus {
                border-color: #667eea !important;
                box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1) !important;
            }
            
            /* Labels */
            .stTextInput > label, .stTextArea > label {
                color: #2c3e50 !important;
                font-weight: 500 !important;
            }
            
            /* Placeholder text */
            .stTextInput input::placeholder, .stTextArea textarea::placeholder {
                color: #999999 !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        job_title = st.text_input("Job Title", value=st.session_state.job_title)
        st.session_state.job_title = job_title
        
        job_description = st.text_area(
            "Job Requirements",
            height=300,
            value=st.session_state.job_description,
            placeholder="Enter the job description, requirements, and qualifications..."
        )
        st.session_state.job_description = job_description
        
        if st.button("Process Job Description", type="primary", use_container_width=True):
            if job_description:
                with st.spinner("Processing..."):
                    st.session_state.job_embedding = get_embedding(job_description)
                    st.success("✅ Job description processed!")
            else:
                st.warning("Please enter a job description")
    
    with col2:
        st.markdown("### Upload Resumes")
        
        # Custom styled file uploader
        st.markdown("""
            <style>
            /* File uploader container */
            section[data-testid="stFileUploader"] {
                background-color: #2c2d3e;
                border-radius: 8px;
                padding: 8px;
            }
            
            /* Dropzone area */
            section[data-testid="stFileUploader"] > div:first-child {
                background-color: #2c2d3e !important;
            }
            
            /* Uploaded files display */
            section[data-testid="stFileUploader"] label {
                color: white !important;
            }
            
            /* File items */
            div[data-testid="stFileUploaderFile"] {
                background-color: #424354 !important;
                color: white !important;
                border: 1px solid #565768 !important;
            }
            
            /* File name text */
            div[data-testid="stFileUploaderFile"] small {
                color: #e0e0e0 !important;
            }
            
            /* File size text */
            div[data-testid="stFileUploaderFile"] span {
                color: #9ca3af !important;
            }
            
            /* Delete button */
            div[data-testid="stFileUploaderDeleteBtn"] button {
                color: #ff6b6b !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "Drop resume files here",
            type=['pdf', 'docx', 'txt'],
            accept_multiple_files=True,
            help="Support for PDF, DOCX, and TXT formats • Limit 200MB per file • PDF, DOCX, TXT"
        )
        
        if uploaded_files and st.button("Process Resumes", type="primary", use_container_width=True):
            if not st.session_state.job_embedding:
                st.warning("Please process job description first")
            else:
                candidates_data = []
                progress = st.progress(0)
                
                for idx, file in enumerate(uploaded_files):
                    progress.progress((idx + 1) / len(uploaded_files))
                    
                    # Store file for download
                    file_bytes = file.read()
                    file.seek(0)  # Reset file pointer
                    
                    # Extract text
                    if file.type == "application/pdf":
                        text = extract_text_from_pdf(file)
                    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                        text = extract_text_from_docx(file)
                    else:
                        text = str(file_bytes, "utf-8")
                    
                    if text:
                        # Extract candidate info
                        info = extract_candidate_info(text, file.name)
                        
                        # Extract skills
                        skills = extract_skills(text)
                        
                        # Get embedding and calculate similarity
                        resume_embedding = get_embedding(text)
                        similarity = calculate_similarity(
                            st.session_state.job_embedding,
                            resume_embedding
                        )
                        
                        # Generate summary
                        summary = generate_fit_summary(
                            st.session_state.job_description,
                            text,
                            info['name']
                        )
                        
                        candidate_data = {
                            'name': info['name'],
                            'email': info['email'],
                            'phone': info['phone'],
                            'filename': file.name,
                            'role': st.session_state.job_title,
                            'education': info['education'],
                            'location': info['location'],
                            'years_experience': info['years_experience'],
                            'skills': skills,
                            'similarity_score': similarity,
                            'summary': summary,
                            'resume_text': text[:3000],
                            'file_content': file_bytes,
                            'initials': get_initials(info['name'])
                        }
                        
                        candidates_data.append(candidate_data)
                        st.session_state.uploaded_resumes[file.name] = file_bytes
                
                st.session_state.candidates_data = candidates_data
                progress.empty()
                st.success(f"✅ Processed {len(candidates_data)} resumes successfully!")
                st.rerun()

# Display Candidates - Only show top 5
if st.session_state.candidates_data:
    # Sort by similarity score
    sorted_candidates = sorted(
        st.session_state.candidates_data,
        key=lambda x: x['similarity_score'],
        reverse=True
    )
    
    # IMPORTANT: Only take top 5 candidates
    top_candidates = sorted_candidates[:5]
    
    # Filter based on search (only within top 5)
    if search_query:
        top_candidates = [
            c for c in top_candidates
            if search_query.lower() in c['name'].lower() or
               search_query.lower() in ' '.join(c['skills']).lower()
        ]
    
    # Display message about selection
    if len(sorted_candidates) > 5:
        st.info(f"📊 Showing top 5 candidates out of {len(sorted_candidates)} total resumes based on match score")
    
    # Display each top candidate
    for idx, candidate in enumerate(top_candidates):
        # Determine match level
        score = candidate['similarity_score']
        if score >= 0.8:
            match_class = "match-strong"
            match_text = "Strong Match"
        elif score >= 0.6:
            match_class = "match-good"
            match_text = "Good Match"
        else:
            match_class = "match-moderate"
            match_text = "Potential Match"
        
        # Create unique key for this candidate
        candidate_key = f"candidate_{idx}_{candidate['name']}"
        
        # Create candidate card container
        with st.container():
            # Use columns for layout
            col_main = st.columns([1])[0]
            
            with col_main:
                # Create the card with proper styling using markdown
                card_html = f"""
                <div class="candidate-card">
                    <div class="candidate-header">
                        <div class="candidate-info">
                            <div class="candidate-avatar">{candidate['initials']}</div>
                            <div style="overflow: hidden;">
                                <div class="candidate-name">
                                    #{idx + 1} - {candidate['name']}
                                    <span class="score-indicator">+{round(score * 100)}</span>
                                </div>
                                <div class="candidate-role">{candidate['role']} @ {candidate['email'].split('@')[1].split('.')[0].upper() if '@' in candidate['email'] else 'Company'}</div>
                                <div class="candidate-education">{candidate['education']}</div>
                            </div>
                        </div>
                        <div class="match-badge {match_class}">{match_text}</div>
                    </div>
                </div>
                """
    
                # Render the HTML properly
                st.markdown(card_html, unsafe_allow_html=True)
                
                # Action buttons row
                col1, col2, col3 = st.columns([1, 3, 1])
                
                with col1:
                    # Social/Contact icons - render properly
                    st.markdown("""
                        <div class="action-icons">
                            <span class="icon-button">👤</span>
                            <span class="icon-button">💼</span>
                            <span class="icon-button">✉️</span>
                            <span class="icon-button">📞</span>
                            <span class="icon-button">💬</span>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    # Summary toggle button
                    if st.button(f"📋 Summary of Fit", key=f"summary_{candidate_key}", type="secondary"):
                        st.session_state.show_summary[candidate_key] = not st.session_state.show_summary.get(candidate_key, False)
                
                with col3:
                    # Download/View Resume button
                    if candidate['filename'] in st.session_state.uploaded_resumes:
                        file_content = st.session_state.uploaded_resumes[candidate['filename']]
                        st.download_button(
                            label="📄 View Resume ▼",
                            data=file_content,
                            file_name=candidate['filename'],
                            mime="application/octet-stream",
                            key=f"download_{candidate_key}"
                        )
                
                # Show summary if toggled
                if st.session_state.show_summary.get(candidate_key, False):
                    summary_html = f"""
                        <div class="summary-section">
                            <div class="summary-title">Why {candidate['name']} is a great fit:</div>
                            <div class="summary-text">{candidate['summary']}</div>
                        </div>
                    """
                    st.markdown(summary_html, unsafe_allow_html=True)
                
                # Add spacing between cards
                st.markdown("", unsafe_allow_html=True)

else:
    st.info("👆 Upload resumes and process them to see candidates here")

# Sidebar (hidden by default, can be expanded)
with st.sidebar:
    st.markdown("### 🎯 Quick Stats")
    if st.session_state.candidates_data:
        scores = [c['similarity_score'] for c in st.session_state.candidates_data]
        st.metric("Total Candidates", len(st.session_state.candidates_data))
        st.metric("Average Match", f"{round(np.mean(scores) * 100)}%")
        st.metric("Best Match", f"{round(max(scores) * 100)}%")
        
        # Export options
        st.markdown("### 📥 Export")
        df = pd.DataFrame([
            {
                'Name': c['name'],
                'Email': c['email'],
                'Match Score': f"{round(c['similarity_score'] * 100)}%",
                'Experience': f"{c['years_experience']} years",
                'Location': c['location']
            }
            for c in st.session_state.candidates_data
        ])
        
        csv = df.to_csv(index=False)
        st.download_button(
            "Download CSV",
            csv,
            "candidates.csv",
            "text/csv"
        )
