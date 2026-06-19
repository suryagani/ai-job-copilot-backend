from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
import json
import smtplib
from io import BytesIO
from email.mime.text import MIMEText
from pathlib import Path
from json_repair import repair_json
from openai import OpenAI
from docx import Document
from docx.shared import Pt
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT

# -----------------------
# Setup
# -----------------------
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError("OPENAI_API_KEY not found. Put it in your .env file.")

client = OpenAI(api_key=api_key)

app = FastAPI(title="AI Job Copilot", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(".")
JOB_ALERT_FILE = DATA_DIR / "job_alert_config.json"

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)

ROLE_CATALOG = [
    "Software Engineer",
    "Backend Developer",
    "Frontend Developer",
    "Full Stack Developer",
    "Mobile App Developer",
    "DevOps Engineer",
    "Cloud Engineer",
    "Site Reliability Engineer",
    "Platform Engineer",
    "Systems Administrator",
    "Network Engineer",
    "Cybersecurity Analyst",
    "IT Support Engineer",
    "QA Engineer",
    "QA Automation Engineer",
    "Automation Engineer",
    "RPA Developer",
    "Data Analyst",
    "Business Analyst",
    "Data Engineer",
    "Data Scientist",
    "BI Analyst",
    "AI / ML Engineer",
    "Machine Learning Engineer",
    "Generative AI Engineer",
    "MLOps Engineer",
    "Product Manager",
    "Project Manager",
    "Program Manager",
    "Scrum Master",
    "Operations Analyst",
    "Operations Executive",
    "Operations Manager",
    "Supply Chain Analyst",
    "Logistics Coordinator",
    "Procurement Specialist",
    "Sales Executive",
    "Business Development Executive",
    "Account Manager",
    "Marketing Executive",
    "Digital Marketing Specialist",
    "SEO Specialist",
    "Content Strategist",
    "Content Writer",
    "Social Media Manager",
    "Graphic Designer",
    "UI/UX Designer",
    "Motion Designer",
    "Recruiter",
    "Talent Acquisition Specialist",
    "HR Executive",
    "HR Generalist",
    "Customer Support Executive",
    "Customer Success Manager",
    "Accountant",
    "Financial Analyst",
    "Finance Executive",
    "Investment Analyst",
    "Audit Associate",
    "Tax Associate",
    "Banking Associate",
    "Administrative Assistant",
    "Executive Assistant",
    "Office Administrator",
    "Legal Associate",
    "Compliance Analyst",
    "Research Assistant",
    "Teacher",
    "Lecturer",
    "Instructional Designer",
    "Healthcare Administrator",
    "Pharmacist",
    "Nurse",
    "Medical Coder",
    "Clinical Data Analyst",
    "Electronics Engineer",
    "Embedded Systems Engineer",
    "VLSI Design Engineer",
    "Telecommunications Engineer",
    "ECE Engineer",
    "Electrical Engineer",
    "Power Systems Engineer",
    "Mechanical Engineer",
    "Automotive Engineer",
    "Manufacturing Engineer",
    "Production Engineer",
    "Industrial Engineer",
    "Civil Engineer",
    "Structural Engineer",
    "Site Engineer",
    "Construction Engineer",
    "Architect",
    "Interior Designer",
    "Environmental Engineer",
    "Chemical Engineer",
    "Process Engineer",
    "Food Technologist",
    "Agriculture Officer",
    "Geologist",
    "Quantity Surveyor",
]


# -----------------------
# Models
# -----------------------
class ProfileInput(BaseModel):
    target_role: str = Field(..., examples=["Python Developer"])
    target_location: str = Field("United Kingdom", examples=["United Kingdom"])
    headline: str = ""
    about: str
    experience: str = ""


class OptimizedProfile(BaseModel):
    headline: str
    about: str
    experience_bullets: list[str]
    top_keywords: list[str]


class LinkedInCopyInput(BaseModel):
    headline: str
    about: str
    experience_bullets: list[str]


class RoleSuggestionInput(BaseModel):
    about: str


class ScratchProfileInput(BaseModel):
    target_role: str
    education: str
    skills: str
    projects: str
    experience: str = ""
    career_goal: str
    target_location: str = "United Kingdom"


class ResumeOptimizerInput(BaseModel):
    target_role: str
    target_country: str = "United Kingdom"
    resume_text: str
    job_description: str = ""
    target_location: str = "United Kingdom"


class ResumeIntelligenceInput(BaseModel):
    full_name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin_url: str = ""
    portfolio_url: str = ""
    target_role: str
    target_country: str = "Global"
    target_industry: str = ""
    career_direction: str = ""
    experience_level: str = ""
    current_background: str = ""
    highest_qualification: str = ""
    education_details: str = ""
    work_experience: str = ""
    internships: str = ""
    projects: str = ""
    technical_skills: str = ""
    transferable_skills: str = ""
    tools_software: str = ""
    certifications: str = ""
    achievements: str = ""
    leadership_experience: str = ""
    career_change: str = "No"
    current_field: str = ""
    target_field: str = ""
    preferred_resume_style: str = "Auto Recommend"


class ResumeOptimizerOutput(BaseModel):
    recommended_resume_style: str
    recommendation_reason: str
    optimized_resume: str
    ats_keywords: list[str]
    weaknesses_found: list[str]
    improvement_suggestions: list[str]
    ats_score_estimate: str


class ResumeExportSection(BaseModel):
    heading: str
    body: str


class ResumeExportInput(BaseModel):
    full_name: str = ""
    target_role: str = ""
    target_country: str = "United Kingdom"
    sections: list[ResumeExportSection]


class HiringMessageInput(BaseModel):
    target_role: str
    company_name: str
    hiring_manager_name: str = ""
    job_context: str = ""
    personal_background: str
    target_location: str = "United Kingdom"


class HiringMessageOutput(BaseModel):
    connection_message: str
    outreach_message: str
    follow_up_message: str


class JobAlertInput(BaseModel):
    email: str
    target_role: str
    country: str
    city: str
    experience_level: str
    keywords: str = ""
    preferred_time: str = "09:00"


class JobAlertTestOutput(BaseModel):
    status: str
    message: str
    preview_subject: str
    preview_body: str


# -----------------------
# Helpers
# -----------------------
def parse_json_response(content: str) -> dict:
    try:
        return json.loads(content)
    except Exception:
        try:
            fixed = repair_json(content)
            return json.loads(fixed)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Model returned invalid JSON. Error: {e}. Raw output: {content[:1000]}",
            )


def save_json_file(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_json_file(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def get_country_template_settings(country: str) -> dict:
    normalized = (country or "").strip().lower()
    default_settings = {
        "page_size": A4,
        "summary_heading": "Professional Summary",
        "skills_heading": "Key Skills",
    }

    if "united states" in normalized or "canada" in normalized:
        return {
            "page_size": letter,
            "summary_heading": "Professional Summary",
            "skills_heading": "Core Skills",
        }

    if "australia" in normalized:
        return {
            "page_size": A4,
            "summary_heading": "Career Summary",
            "skills_heading": "Key Skills",
        }

    if "germany" in normalized:
        return {
            "page_size": A4,
            "summary_heading": "Professional Profile",
            "skills_heading": "Core Competencies",
        }

    return default_settings


def normalize_export_sections(sections: list[ResumeExportSection], country: str) -> list[ResumeExportSection]:
    settings = get_country_template_settings(country)
    normalized = []
    for section in sections:
        heading = section.heading.strip()
        if heading.lower() in {"summary", "professional summary"}:
            heading = settings["summary_heading"]
        elif heading.lower() in {"skills", "key skills"}:
            heading = settings["skills_heading"]

        body = section.body.strip()
        if body:
            normalized.append(ResumeExportSection(heading=heading, body=body))

    return normalized


def build_docx_resume(export: ResumeExportInput) -> BytesIO:
    settings = get_country_template_settings(export.target_country)
    sections = normalize_export_sections(export.sections, export.target_country)

    document = Document()
    normal_style = document.styles["Normal"]
    normal_style.font.name = "Calibri"
    normal_style.font.size = Pt(11)

    title = export.full_name.strip() or export.target_role.strip() or "Resume"
    title_paragraph = document.add_paragraph()
    title_run = title_paragraph.add_run(title)
    title_run.bold = True
    title_run.font.size = Pt(18)

    if export.target_role.strip():
      subtitle = document.add_paragraph()
      subtitle_run = subtitle.add_run(export.target_role.strip())
      subtitle_run.italic = True
      subtitle_run.font.size = Pt(11)

    for section in sections:
        heading = document.add_paragraph()
        heading_run = heading.add_run(section.heading)
        heading_run.bold = True
        heading_run.font.size = Pt(12)

        for line in section.body.splitlines():
            cleaned = line.strip()
            if not cleaned:
                continue
            if cleaned.startswith("- ") or cleaned.startswith("* "):
                document.add_paragraph(cleaned[2:].strip(), style="List Bullet")
            else:
                document.add_paragraph(cleaned)

    buffer = BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer


def build_pdf_resume(export: ResumeExportInput) -> BytesIO:
    settings = get_country_template_settings(export.target_country)
    sections = normalize_export_sections(export.sections, export.target_country)
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=settings["page_size"],
        leftMargin=42,
        rightMargin=42,
        topMargin=42,
        bottomMargin=42,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ResumeTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        alignment=TA_LEFT,
        spaceAfter=8,
    )
    subtitle_style = ParagraphStyle(
        "ResumeSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=10,
        leading=13,
        textColor="#334155",
        spaceAfter=8,
    )
    heading_style = ParagraphStyle(
        "ResumeHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        spaceBefore=8,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "ResumeBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        spaceAfter=3,
    )

    story = []
    title = export.full_name.strip() or export.target_role.strip() or "Resume"
    story.append(Paragraph(title, title_style))

    if export.target_role.strip():
        story.append(Paragraph(export.target_role.strip(), subtitle_style))

    story.append(Spacer(1, 8))

    for section in sections:
        story.append(Paragraph(section.heading, heading_style))
        for line in section.body.splitlines():
            cleaned = line.strip()
            if not cleaned:
                continue
            if cleaned.startswith("- ") or cleaned.startswith("* "):
                cleaned = f"&bull; {cleaned[2:].strip()}"
            story.append(Paragraph(cleaned.replace("\n", "<br/>"), body_style))
        story.append(Spacer(1, 4))

    doc.build(story)
    buffer.seek(0)
    return buffer


def build_job_alert_preview(data: JobAlertInput) -> tuple[str, str]:
    subject = f"AI Job Copilot Daily Job Alert - {data.target_role}"
    body = f"""Hello,

Your daily AI Job Copilot alert is configured successfully.

Target role: {data.target_role}
Country: {data.country}
City / Location: {data.city}
Experience level: {data.experience_level}
Keywords: {data.keywords or "Not specified"}
Preferred send time: {data.preferred_time}

This is a test/preview email for your job alert setup.

Next production step:
- connect a real job source or API
- run a scheduler daily
- send matched jobs automatically to this inbox

Thanks,
AI Job Copilot
"""
    return subject, body


def send_email(to_email: str, subject: str, body: str) -> None:
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASSWORD or not SMTP_FROM:
        raise RuntimeError("SMTP is not configured.")

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = SMTP_FROM
    msg["To"] = to_email

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_FROM, [to_email], msg.as_string())


# -----------------------
# Routes
# -----------------------
@app.get("/")
def home():
    return {"status": "running", "service": "ai-job-copilot"}


@app.post("/suggest-role")
def suggest_role(data: RoleSuggestionInput):
    system_msg = (
        "You are a career assistant for job seekers across technical and non-technical fields. "
        "Read the user's About section and suggest the single best professional role title. "
        "Use the broad role catalog as guidance, but if a better common professional title is needed, "
        "return that role title instead. "
        "Return only one concise role name and nothing else."
    )

    user_msg = f"""
Reference role catalog:
{ROLE_CATALOG}

User About section:
{data.about}

Choose the single best matching professional role title.
Return only the role name.
"""

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        temperature=0,
    )

    suggested_role = (resp.choices[0].message.content or "").strip()
    if not suggested_role or len(suggested_role) > 80:
        raise HTTPException(status_code=500, detail=f"Invalid suggested role returned: {suggested_role}")

    return {"suggested_role": suggested_role}


@app.post("/optimize-profile", response_model=OptimizedProfile)
def optimize_profile(data: ProfileInput):
    system_msg = (
        "You are an expert LinkedIn profile strategist for the job market specified by the user. "
        "You optimize profiles for recruiter clarity, keyword relevance, and professional positioning. "
        "The user's About section is the primary source of truth. "
        "You must NEVER invent employers, dates, certifications, achievements, metrics, tools, or projects "
        "that are not clearly supported by the input. "
        "Your job is to improve wording, structure, clarity, and positioning for the target role."
    )

    user_msg = f"""
Target role: {data.target_role}
Target job market / country: {data.target_location}

Primary source input (About section):
{data.about}

Your tasks:
1. Create a LinkedIn headline tailored to the target role.
2. Rewrite the About section in a strong professional tone suitable for the target job market.
3. Keep the About section natural, confident, and recruiter-friendly.
4. Highlight transferable strengths already present in the input.
5. Generate 10-15 relevant LinkedIn/ATS keywords.
6. Do not use emojis.
7. Do not invent facts.
8. If the input is limited, improve presentation but stay truthful.

Headline rules:
- Max 220 characters
- Must be role-first
- Should sound modern and recruiter-friendly
- Avoid generic phrases like "looking for opportunities" unless strongly needed

About rules:
- 120 to 180 words
- Clear opening line
- Mention strengths, tools, and direction only if supported by input
- Make it sound polished but human

Return ONLY valid JSON in this exact format:
{{
  "headline": "string",
  "about": "string",
  "experience_bullets": [],
  "top_keywords": ["keyword1", "keyword2", "keyword3"]
}}
"""

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.2,
    )

    content = (resp.choices[0].message.content or "").strip()
    parsed = parse_json_response(content)

    required_keys = {"headline", "about", "experience_bullets", "top_keywords"}
    if not required_keys.issubset(parsed.keys()):
        raise HTTPException(
            status_code=500,
            detail=f"Missing keys in model response. Required: {required_keys}. Got: {list(parsed.keys())}",
        )

    if not isinstance(parsed["experience_bullets"], list):
        parsed["experience_bullets"] = []

    if not isinstance(parsed["top_keywords"], list):
        raise HTTPException(status_code=500, detail="top_keywords must be a list.")

    parsed["top_keywords"] = [str(x).strip() for x in parsed["top_keywords"] if str(x).strip()]
    return parsed


@app.post("/generate-profile-from-scratch", response_model=OptimizedProfile)
def generate_profile_from_scratch(data: ScratchProfileInput):
    system_msg = (
        "You are an expert LinkedIn profile strategist for freshers, students, early-career professionals, "
        "and career switchers in the user's target job market. "
        "Your task is to create a strong LinkedIn headline, About section, and keywords from structured user inputs. "
        "You must NEVER invent employers, dates, certifications, achievements, metrics, tools, projects, "
        "or experience that are not clearly supported by the user input. "
        "You should write in a professional, recruiter-friendly style and align the profile to the target role."
    )

    user_msg = f"""
Target role: {data.target_role}
Target job market / country: {data.target_location}

User details:
Education:
{data.education}

Skills:
{data.skills}

Projects:
{data.projects}

Experience:
{data.experience}

Career goal:
{data.career_goal}

Your tasks:
1. Create a LinkedIn headline tailored to the target role.
2. Write a strong LinkedIn About section from scratch using only the provided details.
3. Generate 10-15 relevant LinkedIn/ATS keywords.
4. Do not use emojis.
5. Do not invent facts.
6. If experience is limited, present the profile confidently but truthfully.

Headline rules:
- Max 220 characters
- Must be role-first
- Clear, modern, recruiter-friendly
- Avoid weak phrases like "looking for opportunities" unless needed

About rules:
- 120 to 180 words
- Clear opening line
- Mention education, skills, projects, experience, and goal only if provided
- Sound professional, confident, and natural

Return ONLY valid JSON in this exact format:
{{
  "headline": "string",
  "about": "string",
  "experience_bullets": [],
  "top_keywords": ["keyword1", "keyword2", "keyword3"]
}}
"""

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.2,
    )

    content = (resp.choices[0].message.content or "").strip()
    parsed = parse_json_response(content)

    required_keys = {"headline", "about", "experience_bullets", "top_keywords"}
    if not required_keys.issubset(parsed.keys()):
        raise HTTPException(
            status_code=500,
            detail=f"Missing keys in model response. Required: {required_keys}. Got: {list(parsed.keys())}",
        )

    if not isinstance(parsed["experience_bullets"], list):
        parsed["experience_bullets"] = []

    if not isinstance(parsed["top_keywords"], list):
        raise HTTPException(status_code=500, detail="top_keywords must be a list.")

    parsed["top_keywords"] = [str(x).strip() for x in parsed["top_keywords"] if str(x).strip()]
    return parsed


@app.post("/optimize-resume", response_model=ResumeOptimizerOutput)
def optimize_resume(data: ResumeOptimizerInput):
    system_msg = (
        "You are a senior professional resume writer, ATS optimization specialist, and resume rebuilder with 15 years of experience. "
        "Your job is to analyze an existing resume and rebuild it into a stronger, recruiter-quality, ATS-friendly resume. "
        "You must think like a recruiter, hiring manager, ATS parser, and career strategist before writing. "
        "You must NEVER invent employers, dates, certifications, achievements, metrics, tools, projects, or responsibilities not supported by the user's resume text. "
        "If a job description is provided, align the wording and keyword emphasis to it, but remain truthful. "
        "Adapt tone and structure to the target role, target country, and likely seniority level suggested by the input. "
        "Do not create generic AI summaries. Return a complete optimized resume, not just fragments. "
        "Never include labels like Template: India, Template: UK, preview, backend, or test in the output. "
        "Use clean ATS-safe structure, strong action verbs, clear role alignment, and keyword relevance. "
        "Avoid tables, columns, icons, graphics, or decorative formatting guidance."
    )

    user_msg = f"""
Target role: {data.target_role}
Target country / job market: {data.target_country}

Resume text:
{data.resume_text}

Optional Job Description:
{data.job_description}

Tasks:
1. Analyze the current resume and identify the biggest weaknesses blocking recruiter impact or ATS performance.
2. Recommend the best resume style for this candidate based on the content, target role, target country, and likely experience level inferred from the resume.
3. Explain briefly why that style is suitable.
4. Rewrite the entire resume professionally into a complete ATS-friendly version.
5. Tailor the wording to the target role and job market.
6. If a job description is provided, prioritize matching terminology where truthful.
7. Group skills and competencies in a cleaner, more recruiter-friendly structure.
8. Strengthen weak bullet points into clearer impact-oriented statements only when supported by the user's content.
9. Do not invent facts.
10. Do not use emojis.
11. Do not include Template labels or developer/testing language.

Resume rebuild rules:
- Include a clear header/contact section if details exist in the pasted resume
- Include a professional title aligned to the target role when supported
- Include a professional summary
- Include key skills or core competencies
- Include professional experience / relevant experience
- Include projects if relevant content exists
- Include education if present
- Include certifications if present
- Keep it ATS-friendly and paste-ready

ATS score estimate rules:
- Provide a short estimate like "High ATS readiness (82-88/100 range)" or "Moderate ATS readiness (68-75/100 range)"
- This is an internal estimate, not a guaranteed external ATS score

Return ONLY valid JSON in this exact format:
{{
  "recommended_resume_style": "string",
  "recommendation_reason": "string",
  "optimized_resume": "string",
  "ats_keywords": ["keyword1", "keyword2", "keyword3"],
  "weaknesses_found": ["weakness1", "weakness2"],
  "improvement_suggestions": ["suggestion1", "suggestion2"],
  "ats_score_estimate": "string"
}}
"""

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.2,
    )

    content = (resp.choices[0].message.content or "").strip()
    parsed = parse_json_response(content)

    required_keys = {
        "recommended_resume_style",
        "recommendation_reason",
        "optimized_resume",
        "ats_keywords",
        "weaknesses_found",
        "improvement_suggestions",
        "ats_score_estimate",
    }
    if not required_keys.issubset(parsed.keys()):
        raise HTTPException(
            status_code=500,
            detail=f"Missing keys in model response. Required: {required_keys}. Got: {list(parsed.keys())}",
        )

    if not isinstance(parsed["ats_keywords"], list):
        parsed["ats_keywords"] = []
    if not isinstance(parsed["weaknesses_found"], list):
        parsed["weaknesses_found"] = []
    if not isinstance(parsed["improvement_suggestions"], list):
        parsed["improvement_suggestions"] = []

    parsed["ats_keywords"] = [str(x).strip() for x in parsed["ats_keywords"] if str(x).strip()]
    parsed["weaknesses_found"] = [str(x).strip() for x in parsed["weaknesses_found"] if str(x).strip()]
    parsed["improvement_suggestions"] = [str(x).strip() for x in parsed["improvement_suggestions"] if str(x).strip()]
    return parsed


@app.post("/build-resume")
def build_resume(data: ResumeIntelligenceInput):
    system_msg = (
        "You are a senior professional resume writer, ATS specialist, and career strategist with 15 years of experience. "
        "Your job is to create outstanding, recruiter-quality resumes that can compete with professional resume-writing services. "
        "You must think like a hiring manager, recruiter, ATS system, and career coach before writing. "
        "The resume must be tailored to the target role, target country, target industry, experience level, and career direction. "
        "Do not create generic AI summaries. "
        "Do not invent fake facts, employers, dates, degrees, certifications, metrics, achievements, or experience. "
        "If information is missing, write honestly and make the candidate sound strong using only provided details. "
        "If the user is changing careers, translate their previous background into transferable skills relevant to the target role. "
        "Never include labels like Template: India or Template: UK in the resume. "
        "Use clean ATS-friendly formatting with standard headings."
    )

    user_msg = f"""
Create a professional resume using the following candidate information.

Candidate Details:
Full Name: {data.full_name}
Email: {data.email}
Phone: {data.phone}
Location: {data.location}
LinkedIn: {data.linkedin_url}
Portfolio/GitHub: {data.portfolio_url}

Target Strategy:
Target Role: {data.target_role}
Target Country: {data.target_country}
Target Industry: {data.target_industry}
Career Direction: {data.career_direction}
Experience Level: {data.experience_level}
Preferred Resume Style: {data.preferred_resume_style}

Background:
Current Background: {data.current_background}
Highest Qualification: {data.highest_qualification}
Education Details:
{data.education_details}

Work Experience:
{data.work_experience}

Internships:
{data.internships}

Projects:
{data.projects}

Skills:
Technical Skills:
{data.technical_skills}

Transferable Skills:
{data.transferable_skills}

Tools / Software:
{data.tools_software}

Certifications:
{data.certifications}

Achievements:
{data.achievements}

Leadership / Team Experience:
{data.leadership_experience}

Career Change:
Career Change: {data.career_change}
Current Field: {data.current_field}
Target Field: {data.target_field}

Instructions:
1. First recommend the best resume style if preferred_resume_style is Auto Recommend.
   Allowed resume styles:
   - Graduate ATS Resume
   - Technical Professional Resume
   - Career Switcher Resume
   - Senior Professional Resume
   - Executive Resume
   - One Page ATS Resume
   - Country-Specific Professional Resume
   If the user selects a specific style instead of Auto Recommend, keep the recommendation aligned to that chosen style.
2. Explain briefly why that style is suitable.
3. Generate a complete, polished, ATS-friendly resume.
4. The resume should feel like it was written by a professional resume writer with 10–15 years of experience.
5. The resume should be role-specific, country-aware, and market-ready.
6. Use strong professional language, but remain truthful.
7. Group skills into meaningful clusters.
8. Convert weak responsibilities into achievement-style bullets where supported by input.
9. If no metrics are provided, do not fabricate numbers. Use impact-based language without fake metrics.
10. Use standard resume headings.
11. Do not include hobbies unless highly relevant.
12. Do not include "Template: country" text.
13. Do not include developer or testing language.

Resume section rules:
- Header with name and contact details
- Professional Title aligned to target role
- Professional Summary
- Core Competencies / Key Skills
- Professional Experience or Relevant Experience
- Projects
- Education
- Certifications
- Additional Information only if useful

Return ONLY valid JSON in this exact format:
{{
  "recommended_resume_style": "string",
  "recommendation_reason": "string",
  "professional_title": "string",
  "full_resume": "string",
  "ats_keywords": ["keyword1", "keyword2"],
  "strengths": ["strength1", "strength2"],
  "improvement_suggestions": ["suggestion1", "suggestion2"]
}}
"""

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.2,
    )

    content = (resp.choices[0].message.content or "").strip()
    parsed = parse_json_response(content)

    required_keys = {
        "recommended_resume_style",
        "recommendation_reason",
        "professional_title",
        "full_resume",
        "ats_keywords",
        "strengths",
        "improvement_suggestions",
    }

    if not required_keys.issubset(parsed.keys()):
        raise HTTPException(
            status_code=500,
            detail=f"Missing keys in resume builder response. Required: {required_keys}. Got: {list(parsed.keys())}",
        )

    if not isinstance(parsed["ats_keywords"], list):
        parsed["ats_keywords"] = []
    if not isinstance(parsed["strengths"], list):
        parsed["strengths"] = []
    if not isinstance(parsed["improvement_suggestions"], list):
        parsed["improvement_suggestions"] = []

    return parsed


@app.post("/export-resume-docx")
def export_resume_docx(data: ResumeExportInput):
    buffer = build_docx_resume(data)
    filename = f"{(data.full_name or data.target_role or 'resume').strip().replace(' ', '-').lower()}-resume.docx"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers,
    )


@app.post("/export-resume-pdf")
def export_resume_pdf(data: ResumeExportInput):
    buffer = build_pdf_resume(data)
    filename = f"{(data.full_name or data.target_role or 'resume').strip().replace(' ', '-').lower()}-resume.pdf"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers=headers,
    )


@app.post("/generate-hiring-messages", response_model=HiringMessageOutput)
def generate_hiring_messages(data: HiringMessageInput):
    system_msg = (
        "You are an expert career communication assistant for the user's target job market. "
        "Your job is to generate short, polite, professional outreach messages for LinkedIn or email. "
        "You must NEVER invent achievements, years of experience, or technical skills not supported by the user's background. "
        "Messages should feel human, confident, and respectful—not spammy or over-salesy."
    )

    user_msg = f"""
Target role: {data.target_role}
Company name: {data.company_name}
Hiring manager name: {data.hiring_manager_name}
Target location / country: {data.target_location}

Optional job context:
{data.job_context}

Personal background:
{data.personal_background}

Tasks:
1. Write a short LinkedIn connection request message.
2. Write a slightly longer direct outreach message.
3. Write a polite follow-up message if no reply is received.

Rules:
- Keep messages professional and concise.
- Do not use emojis.
- Do not sound desperate.
- Do not invent facts.
- Mention the role and company naturally.
- The follow-up should be polite and low-pressure.

Return ONLY valid JSON in this exact format:
{{
  "connection_message": "string",
  "outreach_message": "string",
  "follow_up_message": "string"
}}
"""

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.3,
    )

    content = (resp.choices[0].message.content or "").strip()
    parsed = parse_json_response(content)

    required_keys = {"connection_message", "outreach_message", "follow_up_message"}
    if not required_keys.issubset(parsed.keys()):
        raise HTTPException(
            status_code=500,
            detail=f"Missing keys in message response. Required: {required_keys}. Got: {list(parsed.keys())}",
        )

    return parsed


@app.post("/save-job-alert")
def save_job_alert(data: JobAlertInput):
    save_json_file(JOB_ALERT_FILE, data.model_dump())
    return {"status": "saved", "message": "Job alert preferences saved successfully."}


@app.post("/send-test-job-alert", response_model=JobAlertTestOutput)
def send_test_job_alert(data: JobAlertInput):
    subject, body = build_job_alert_preview(data)
    save_json_file(JOB_ALERT_FILE, data.model_dump())

    if SMTP_HOST and SMTP_USER and SMTP_PASSWORD and SMTP_FROM:
        try:
            send_email(data.email, subject, body)
            return JobAlertTestOutput(
                status="sent",
                message="Test email sent successfully.",
                preview_subject=subject,
                preview_body=body,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to send test email: {e}")

    return JobAlertTestOutput(
        status="preview_only",
        message="SMTP is not configured yet. Preview generated successfully.",
        preview_subject=subject,
        preview_body=body,
    )


@app.get("/job-alert-config")
def get_job_alert_config():
    data = load_json_file(JOB_ALERT_FILE)
    return {"status": "ok", "config": data}


@app.post("/format-linkedin")
def format_linkedin(data: LinkedInCopyInput):
    exp = "\n".join([f"• {b}" for b in data.experience_bullets])

    copy_text = f"""HEADLINE
{data.headline}

ABOUT
{data.about}

EXPERIENCE HIGHLIGHTS
{exp}
"""

    return {"copy_text": copy_text}
