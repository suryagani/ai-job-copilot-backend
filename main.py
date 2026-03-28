from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
import json
import smtplib
from email.mime.text import MIMEText
from pathlib import Path
from json_repair import repair_json
from openai import OpenAI

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
    resume_text: str
    job_description: str = ""
    target_location: str = "United Kingdom"


class ResumeOptimizerOutput(BaseModel):
    summary: str
    experience: str
    projects: str
    ats_keywords: list[str]


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
    location: str
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


def build_job_alert_preview(data: JobAlertInput) -> tuple[str, str]:
    subject = f"AI Job Copilot Daily Job Alert - {data.target_role}"
    body = f"""Hello,

Your daily AI Job Copilot alert is configured successfully.

Target role: {data.target_role}
Location: {data.location}
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
    allowed_roles = [
        "Software Engineer",
        "Backend Developer",
        "Python Developer",
        "Full Stack Developer",
        "DevOps Engineer",
        "Cloud Engineer",
        "Data Analyst",
        "Data Engineer",
        "QA Automation Engineer",
        "RPA Developer",
        "AI / ML Engineer",
        "Generative AI Engineer",
        "Automation Engineer",
        "Platform Engineer",
        "MLOps Engineer"
    ]

    system_msg = (
        "You are a career assistant for LinkedIn optimization. "
        "Read the user's About section and choose the single best matching role "
        "from the allowed roles list. "
        "Return only one exact role name from the list and nothing else."
    )

    user_msg = f"""
Allowed roles:
{allowed_roles}

User About section:
{data.about}

Choose the single best matching role from the allowed roles list.
Return only the exact role name.
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

    if suggested_role not in allowed_roles:
        raise HTTPException(status_code=500, detail=f"Invalid suggested role returned: {suggested_role}")

    return {"suggested_role": suggested_role}


@app.post("/optimize-profile", response_model=OptimizedProfile)
def optimize_profile(data: ProfileInput):
    system_msg = (
        "You are an expert LinkedIn profile strategist for the UK job market. "
        "You optimize profiles for recruiter clarity, keyword relevance, and professional positioning. "
        "The user's About section is the primary source of truth. "
        "You must NEVER invent employers, dates, certifications, achievements, metrics, tools, or projects "
        "that are not clearly supported by the input. "
        "Your job is to improve wording, structure, clarity, and positioning for the target role."
    )

    user_msg = f"""
Target role: {data.target_role}
Target location: {data.target_location}

Primary source input (About section):
{data.about}

Your tasks:
1. Create a LinkedIn headline tailored to the target role.
2. Rewrite the About section in a strong UK-professional tone.
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
        "and career switchers in the UK job market. "
        "Your task is to create a strong LinkedIn headline, About section, and keywords from structured user inputs. "
        "You must NEVER invent employers, dates, certifications, achievements, metrics, tools, projects, "
        "or experience that are not clearly supported by the user input. "
        "You should write in a professional, recruiter-friendly style and align the profile to the target role."
    )

    user_msg = f"""
Target role: {data.target_role}
Target location: {data.target_location}

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
        "You are an expert ATS resume optimizer for the UK job market. "
        "You improve resumes for recruiter readability and ATS alignment. "
        "You must NEVER invent employers, dates, certifications, achievements, metrics, tools, projects, "
        "or responsibilities not supported by the user's resume text. "
        "If a job description is provided, align the wording and keyword emphasis to it, but remain truthful. "
        "You should separate improvements into summary, experience, projects, and ATS keywords."
    )

    user_msg = f"""
Target role: {data.target_role}
Target location: {data.target_location}

Resume text:
{data.resume_text}

Optional Job Description:
{data.job_description}

Tasks:
1. Create an ATS-friendly professional summary tailored to the target role.
2. Improve the experience section wording in a concise, recruiter-friendly way.
3. Improve the projects section wording with stronger action verbs and clearer technical framing.
4. Generate 12-18 ATS keywords based on the resume and job description if available.
5. Do not invent facts.
6. Do not use emojis.
7. If job description is provided, prioritize matching terminology where truthful.

Summary rules:
- 60 to 120 words
- Role-aligned
- Professional and clear

Experience rules:
- Return as plain text suitable for pasting into a resume
- Improve clarity and action verbs
- Do not fabricate metrics

Projects rules:
- Return as plain text suitable for pasting into a resume
- Highlight purpose, tools, and technical relevance when present
- Do not fabricate outcomes

Return ONLY valid JSON in this exact format:
{{
  "summary": "string",
  "experience": "string",
  "projects": "string",
  "ats_keywords": ["keyword1", "keyword2", "keyword3"]
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

    required_keys = {"summary", "experience", "projects", "ats_keywords"}
    if not required_keys.issubset(parsed.keys()):
        raise HTTPException(
            status_code=500,
            detail=f"Missing keys in model response. Required: {required_keys}. Got: {list(parsed.keys())}",
        )

    if not isinstance(parsed["ats_keywords"], list):
        raise HTTPException(status_code=500, detail="ats_keywords must be a list.")

    parsed["ats_keywords"] = [str(x).strip() for x in parsed["ats_keywords"] if str(x).strip()]
    return parsed


@app.post("/generate-hiring-messages", response_model=HiringMessageOutput)
def generate_hiring_messages(data: HiringMessageInput):
    system_msg = (
        "You are an expert career communication assistant for the UK job market. "
        "Your job is to generate short, polite, professional outreach messages for LinkedIn or email. "
        "You must NEVER invent achievements, years of experience, or technical skills not supported by the user's background. "
        "Messages should feel human, confident, and respectful—not spammy or over-salesy."
    )

    user_msg = f"""
Target role: {data.target_role}
Company name: {data.company_name}
Hiring manager name: {data.hiring_manager_name}
Target location: {data.target_location}

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