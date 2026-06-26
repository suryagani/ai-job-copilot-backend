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


class ResumeIntelligenceRequest(BaseModel):
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


class ResumeSkillGroup(BaseModel):
    category: str
    skills: list[str]


class ResumeIntelligenceAnalysisOutput(BaseModel):
    candidate_profile_type: str
    career_direction_detected: str
    career_change_detected: bool
    recommended_resume_model: str
    resume_length_rule: str
    target_market_strategy: str
    recruiter_positioning: str
    priority_sections: list[str]
    sections_to_minimize_or_remove: list[str]
    skill_grouping_strategy: list[ResumeSkillGroup]
    ats_keyword_strategy: list[str]
    missing_information: list[str]
    content_risk_flags: list[str]
    writing_guidance: str


class ResumeBuildOutput(BaseModel):
    recommended_resume_style: str
    recommendation_reason: str
    professional_title: str
    resume_length_rule: str
    target_market_strategy: str
    recruiter_positioning: str
    full_resume: str
    ats_keywords: list[str]
    skill_groups: list[ResumeSkillGroup]
    strengths: list[str]
    missing_information: list[str]
    improvement_suggestions: list[str]


class ResumeOptimizerOutput(BaseModel):
    recommended_resume_style: str
    recommendation_reason: str
    optimized_resume: str
    ats_keywords: list[str]
    strengths: list[str]
    weaknesses_found: list[str]
    improvement_suggestions: list[str]
    ats_score_estimate: str


class ResumeReviewerInput(BaseModel):
    resume_text: str
    target_role: str = ""
    target_country: str = "Global ATS"
    job_description: str = ""


class ResumeReviewerOutput(BaseModel):
    ats_score_estimate: str
    score_reason: str
    missing_keywords: list[str]
    weak_sections: list[str]
    strong_sections: list[str]
    recruiter_feedback: str
    improvement_suggestions: list[str]


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


def get_country_rules(country: str) -> str:
    normalized = (country or "").strip().lower()

    if "united states" in normalized or normalized == "usa":
        return (
            "Use a concise, impact-first US style: sharp professional summary, strong action verbs, "
            "keyword-dense skills, and a one-page preference unless seniority clearly justifies more."
        )
    if "canada" in normalized:
        return (
            "Use a clean Canadian professional style: strong summary, direct accomplishments, ATS-safe headings, "
            "and clear relevance to the target role."
        )
    if "united kingdom" in normalized or normalized == "uk":
        return (
            "Use a UK recruiter-friendly style: polished summary, clear responsibilities translated into results, "
            "and practical, professional wording without inflated claims."
        )
    if "australia" in normalized:
        return (
            "Use an Australia-ready style: practical professional summary, results-oriented bullet points, "
            "and strong relevance to the local job market."
        )
    if "germany" in normalized:
        return (
            "Use a structured Germany-aware style: precise wording, orderly sectioning, and strong emphasis on qualifications, "
            "technical credibility, and role alignment."
        )
    if "uae" in normalized or "united arab emirates" in normalized:
        return (
            "Use a UAE recruiter-friendly style: leadership, coordination, execution, and business impact should be clear, "
            "with polished and professional language suited to international employers."
        )

    return (
        "Use a global ATS-safe style: clean headings, role-first positioning, strong recruiter readability, "
        "and broad market-ready language without regional template labels."
    )


def get_resume_length_rules(experience_level: str) -> str:
    normalized = (experience_level or "").strip().lower()
    if normalized in {"student", "fresher"}:
        return "Maximum 1 page. Prioritize education, internships, projects, and the strongest role-relevant skills."
    if normalized in {"1–3 years", "1-3 years", "3–5 years", "3-5 years"}:
        return "Keep it to 1 page. Prioritize the most relevant experience, impact, and skills."
    if normalized in {"5–10 years", "5-10 years"}:
        return "Target 1 to 2 pages maximum. Keep only relevant experience and avoid repetition."
    if normalized in {"10+ years", "10+ yrs", "10+ year"}:
        return "Maximum 2 pages. Focus on leadership, strategic impact, and only the most relevant earlier experience."
    return "Keep the resume concise, relevant, and ATS-friendly with no repetition."


def get_resume_style_models() -> str:
    return (
        "Allowed resume styles:\n"
        "- Graduate ATS Resume\n"
        "- Technical Professional Resume\n"
        "- Career Switcher Resume\n"
        "- Business Professional Resume\n"
        "- Executive Leadership Resume"
    )


def clean_string_list(values) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(value).strip() for value in values if str(value).strip()]


def clean_skill_groups(values) -> list[dict]:
    if not isinstance(values, list):
        return []

    cleaned_groups = []
    for item in values:
        if not isinstance(item, dict):
            continue
        category = str(item.get("category", "")).strip()
        skills = clean_string_list(item.get("skills", []))
        if category and skills:
            cleaned_groups.append({"category": category, "skills": skills})

    return cleaned_groups


def sanitize_resume_text(resume_text: str) -> str:
    banned_markers = [
        "[No formal work experience]",
        "[Details not provided]",
        "[No certifications provided]",
        "[Year not provided]",
        "[Dates Not Provided]",
        "[Confidential Employer]",
        "[Institution Name Not Provided]",
    ]

    cleaned_lines = []
    for raw_line in str(resume_text or "").splitlines():
        line = raw_line.strip()
        if not line:
            if cleaned_lines and cleaned_lines[-1] != "":
                cleaned_lines.append("")
            continue

        normalized_line = line.lower()
        if any(marker.lower() in normalized_line for marker in banned_markers):
            continue
        if normalized_line.startswith("[") and normalized_line.endswith("]"):
            continue
        if "not provided" in normalized_line or "confidential" in normalized_line:
            continue

        cleaned_lines.append(raw_line.rstrip())

    while cleaned_lines and cleaned_lines[-1] == "":
        cleaned_lines.pop()

    return "\n".join(cleaned_lines)


def split_skills_text(*values: str) -> list[str]:
    raw_text = "\n".join(str(value or "") for value in values)
    for separator in [",", ";", "|", "/"]:
        raw_text = raw_text.replace(separator, "\n")

    cleaned = []
    seen = set()
    for item in raw_text.splitlines():
        skill = " ".join(item.strip().split())
        if not skill:
            continue
        key = skill.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(skill)
    return cleaned


def title_case_skill(skill: str) -> str:
    value = str(skill or "").strip()
    if not value:
        return ""
    acronym_map = {
        "aws": "AWS",
        "sql": "SQL",
        "crm": "CRM",
        "erp": "ERP",
        "fpga": "FPGA",
        "vlsi": "VLSI",
        "cmos": "CMOS",
        "rtl": "RTL",
        "cadence": "Cadence",
        "synopsys": "Synopsys",
        "matlab": "MATLAB",
        "git": "Git",
        "linux": "Linux",
    }
    return acronym_map.get(value.lower(), value)


def get_role_skill_targets(target_role: str, career_direction: str, target_industry: str) -> dict:
    role_text = " ".join([target_role or "", career_direction or "", target_industry or ""]).lower()

    if any(keyword in role_text for keyword in ["devops", "sre", "cloud", "platform"]):
        return {
            "categories": [
                ("Cloud & Infrastructure", ["aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible"]),
                ("CI/CD & Automation", ["jenkins", "github actions", "gitlab ci", "bash", "powershell", "git"]),
                ("Programming Languages", ["python", "java", "go", "javascript"]),
                ("Databases", ["sql", "mysql", "postgresql", "mongodb"]),
                ("Operating Systems", ["linux", "unix", "windows server"]),
            ],
            "missing": ["Terraform", "Kubernetes", "CI/CD pipelines", "Monitoring"],
        }
    if any(keyword in role_text for keyword in ["business analyst", "analyst", "reporting"]):
        return {
            "categories": [
                ("Business & Productivity Tools", ["excel", "powerpoint", "google sheets", "power bi", "tableau"]),
                ("Data & Analysis", ["sql", "python", "data analysis", "reporting", "dashboarding"]),
                ("Communication & Documentation", ["communication", "documentation", "presentation", "stakeholder management"]),
                ("Process & Coordination", ["coordination", "requirements gathering", "process improvement"]),
            ],
            "missing": ["Requirements gathering", "Stakeholder management", "Dashboarding"],
        }
    if any(keyword in role_text for keyword in ["vlsi", "embedded", "electronics", "ece"]):
        return {
            "categories": [
                ("VLSI Tools", ["xilinx ise", "modelsim", "cadence", "synopsys", "matlab"]),
                ("Design Flow", ["verilog", "vhdl", "vlsi basics", "cmos", "rtl", "timing analysis", "fpga"]),
                ("Operating Systems", ["linux", "unix", "windows"]),
                ("Core Electronics", ["digital electronics", "embedded c", "embedded systems", "circuit design"]),
                ("Professional Skills", ["problem solving", "analytical thinking", "teamwork", "communication"]),
            ],
            "missing": ["RTL Design", "Timing Analysis", "Cadence", "Synopsys"],
        }
    if any(keyword in role_text for keyword in ["hr", "human resources", "recruit", "talent"]):
        return {
            "categories": [
                ("Business Tools", ["excel", "powerpoint", "google sheets", "documentation", "presentation"]),
                ("Communication & Stakeholder Management", ["communication", "coordination", "teamwork", "stakeholder management"]),
                ("Operations & Coordination", ["scheduling", "onboarding", "event coordination", "coordination"]),
                ("Reporting & Documentation", ["documentation", "reporting", "presentation"]),
            ],
            "missing": ["Employee onboarding", "HR operations", "Recruitment coordination"],
        }
    if any(keyword in role_text for keyword in ["operations manager", "operations", "logistics", "supply chain"]):
        return {
            "categories": [
                ("Operations Management", ["staff scheduling", "inventory coordination", "vendor management", "shift leadership", "service quality management", "process improvement"]),
                ("Leadership & Team Management", ["team supervision", "staff training", "customer handling", "team coordination"]),
                ("Reporting & Business Tools", ["excel", "reporting", "pos systems", "inventory tracking systems"]),
                ("Customer & Service Delivery", ["customer issue resolution", "service quality", "operations coordination"]),
            ],
            "missing": ["Cost control", "Budget oversight", "KPI reporting"],
        }

    if (career_direction or "").strip().lower() == "technical":
        return {
            "categories": [
                ("Technical Skills", ["python", "java", "javascript", "sql", "aws", "docker", "linux"]),
                ("Tools & Platforms", ["git", "excel", "power bi", "tableau", "matlab"]),
                ("Professional Skills", ["problem solving", "analytical thinking", "teamwork", "communication"]),
            ],
            "missing": [],
        }

    return {
        "categories": [
            ("Business Tools", ["excel", "powerpoint", "google sheets", "crm", "erp"]),
            ("Communication & Documentation", ["communication", "documentation", "presentation", "reporting"]),
            ("Operations & Coordination", ["coordination", "scheduling", "stakeholder management", "teamwork"]),
        ],
        "missing": [],
    }


def generate_skill_intelligence(data, intelligence=None):
    role_targets = get_role_skill_targets(
        getattr(data, "target_role", ""),
        getattr(data, "career_direction", "") or (intelligence or {}).get("career_direction_detected", ""),
        getattr(data, "target_industry", ""),
    )
    all_skills = split_skills_text(
        getattr(data, "technical_skills", ""),
        getattr(data, "transferable_skills", ""),
        getattr(data, "tools_software", ""),
    )
    skills_map = {skill.lower(): skill for skill in all_skills}
    used = set()
    skill_groups = []

    for category, keywords in role_targets["categories"]:
        category_skills = []
        for keyword in keywords:
            for skill_lower, original in skills_map.items():
                if skill_lower in used:
                    continue
                if keyword in skill_lower or skill_lower in keyword:
                    category_skills.append(title_case_skill(original))
                    used.add(skill_lower)
                    break
        category_skills = clean_string_list(category_skills)[:8]
        if category_skills:
            skill_groups.append({"category": category, "skills": category_skills})

    remaining = [title_case_skill(original) for skill_lower, original in skills_map.items() if skill_lower not in used]
    remaining = clean_string_list(remaining)

    career_change = str(getattr(data, "career_change", "No")).strip().lower() in {"yes", "true", "1"}
    direction = ((intelligence or {}).get("career_direction_detected") or getattr(data, "career_direction", "") or "").strip().lower()
    if remaining:
        fallback_category = "Transferable Skills" if career_change or direction in {"non-technical", "management", "operations", "sales", "marketing", "finance", "customer support"} else "Additional Tools & Skills"
        skill_groups.append({"category": fallback_category, "skills": remaining[:8]})

    skill_groups = skill_groups[:6]
    priority_skills = []
    for group in skill_groups[:3]:
        priority_skills.extend(group["skills"][:3])
    priority_skills = clean_string_list(priority_skills)[:8]

    missing_role_skills = []
    for skill in role_targets.get("missing", []):
        if skill.lower() not in skills_map:
            missing_role_skills.append(skill)
    missing_role_skills = clean_string_list(missing_role_skills)[:6]

    if career_change:
        skill_positioning_note = "Emphasize transferable skills and business-ready tools first, and keep unrelated technical details secondary unless they directly support the target role."
    elif direction == "technical":
        skill_positioning_note = "Lead with role-critical technical capabilities, then supporting tools, operating environments, and professional strengths."
    else:
        skill_positioning_note = "Prioritize business tools, coordination, communication, reporting, and role-relevant operational strengths ahead of less relevant technical detail."

    return {
        "skill_groups": clean_skill_groups(skill_groups),
        "priority_skills": priority_skills,
        "missing_role_skills": missing_role_skills,
        "skill_positioning_note": skill_positioning_note,
    }


def detect_resume_length_label(experience_level: str) -> str:
    normalized = (experience_level or "").strip().lower()
    if normalized in {"student", "fresher", "1???3 years", "1-3 years", "3???5 years", "3-5 years"}:
        return "One Page"
    if normalized in {"5???10 years", "5-10 years"}:
        return "One to Two Pages"
    if normalized in {"10+ years", "10+ yrs", "10+ year"}:
        return "Two Pages"
    return "One Page"


def detect_career_direction(data: ResumeIntelligenceRequest) -> str:
    preferred = (data.career_direction or "").strip()
    if preferred:
        return preferred

    role_text = " ".join(
        [
            data.target_role,
            data.target_industry,
            data.current_background,
            data.target_field,
        ]
    ).lower()

    keyword_map = [
        ("Management", ["manager", "lead", "director", "head"]),
        ("Sales", ["sales", "account executive", "business development"]),
        ("Marketing", ["marketing", "seo", "content", "brand"]),
        ("Operations", ["operations", "logistics", "supply chain"]),
        ("Finance", ["finance", "account", "audit", "banking"]),
        ("Healthcare", ["healthcare", "nurse", "clinical", "medical"]),
        ("Customer Support", ["customer support", "customer success", "service desk"]),
        ("Technical", ["engineer", "developer", "data", "vlsi", "embedded", "cloud", "software", "it"]),
    ]

    for label, keywords in keyword_map:
        if any(keyword in role_text for keyword in keywords):
            return label

    return "Other"


def get_resume_intelligence_strategy(data: ResumeIntelligenceRequest) -> dict:
    experience = (data.experience_level or "").strip().lower()
    role_text = " ".join(
        [
            data.target_role,
            data.current_background,
            data.work_experience,
            data.leadership_experience,
            data.target_field,
        ]
    ).lower()
    career_change = (data.career_change or "").strip().lower() in {"yes", "true", "1"}
    direction = detect_career_direction(data)

    executive_signal = (
        experience in {"10+ years", "10+ yrs", "10+ year"}
        and any(keyword in role_text for keyword in ["manager", "head", "director", "lead", "operations manager", "restaurant manager"])
    )

    if executive_signal:
        profile_type = "Executive"
        resume_model = "Executive Leadership Resume"
    elif experience in {"10+ years", "10+ yrs", "10+ year", "5???10 years", "5-10 years"}:
        profile_type = "Senior"
        resume_model = "Business Professional Resume" if direction != "Technical" else "Technical Professional Resume"
    elif experience in {"3???5 years", "3-5 years", "1???3 years", "1-3 years"}:
        profile_type = "Early Career" if experience in {"1???3 years", "1-3 years"} else "Mid-Level"
        resume_model = "Technical Professional Resume" if direction == "Technical" else "Business Professional Resume"
    elif experience == "student":
        profile_type = "Student"
        resume_model = "Graduate ATS Resume"
    else:
        profile_type = "Fresher"
        resume_model = "Graduate ATS Resume" if direction == "Technical" else "Business Professional Resume"

    if career_change:
        resume_model = "Career Switcher Resume"

    return {
        "candidate_profile_type": profile_type,
        "career_direction_detected": direction,
        "career_change_detected": career_change,
        "recommended_resume_model": resume_model,
        "resume_length_rule": detect_resume_length_label(data.experience_level),
    }


def normalize_resume_intelligence_result(parsed: dict, data: ResumeIntelligenceRequest) -> dict:
    required_keys = {
        "candidate_profile_type",
        "career_direction_detected",
        "career_change_detected",
        "recommended_resume_model",
        "resume_length_rule",
        "target_market_strategy",
        "recruiter_positioning",
        "priority_sections",
        "sections_to_minimize_or_remove",
        "skill_grouping_strategy",
        "ats_keyword_strategy",
        "missing_information",
        "content_risk_flags",
        "writing_guidance",
    }

    if not required_keys.issubset(parsed.keys()):
        raise HTTPException(
            status_code=500,
            detail=f"Missing keys in resume intelligence response. Required: {required_keys}. Got: {list(parsed.keys())}",
        )

    strategy = get_resume_intelligence_strategy(data)
    parsed["candidate_profile_type"] = strategy["candidate_profile_type"]
    parsed["career_direction_detected"] = strategy["career_direction_detected"]
    parsed["career_change_detected"] = strategy["career_change_detected"]
    parsed["recommended_resume_model"] = strategy["recommended_resume_model"]
    parsed["resume_length_rule"] = strategy["resume_length_rule"]

    career_change_detected = parsed.get("career_change_detected", False)
    if isinstance(career_change_detected, str):
        parsed["career_change_detected"] = career_change_detected.strip().lower() in {"true", "yes", "1"}
    else:
        parsed["career_change_detected"] = bool(career_change_detected)

    parsed["priority_sections"] = clean_string_list(parsed.get("priority_sections", []))
    parsed["sections_to_minimize_or_remove"] = clean_string_list(parsed.get("sections_to_minimize_or_remove", []))
    parsed["skill_grouping_strategy"] = clean_skill_groups(parsed.get("skill_grouping_strategy", []))
    parsed["ats_keyword_strategy"] = clean_string_list(parsed.get("ats_keyword_strategy", []))
    parsed["missing_information"] = clean_string_list(parsed.get("missing_information", []))
    parsed["content_risk_flags"] = clean_string_list(parsed.get("content_risk_flags", []))
    parsed["target_market_strategy"] = str(parsed.get("target_market_strategy", "")).strip()
    parsed["recruiter_positioning"] = str(parsed.get("recruiter_positioning", "")).strip()
    parsed["writing_guidance"] = str(parsed.get("writing_guidance", "")).strip()

    return parsed


def generate_resume_intelligence(data: ResumeIntelligenceRequest) -> dict:
    country_rules = get_country_rules(data.target_country)
    length_rules = get_resume_length_rules(data.experience_level)
    system_msg = (
        "You are a senior career strategist, ATS specialist, recruiter, and resume architect. "
        "Your task is NOT to write the resume. "
        "Your task is to analyze the candidate profile and create a structured resume strategy. "
        "Think like a professional resume writer before writing begins. "
        "Do not invent facts. "
        "Be specific to target role, country, industry, experience level, and career direction."
    )

    user_msg = f"""
Analyze this candidate for resume strategy.

Target Role: {data.target_role}
Target Country: {data.target_country}
Target Industry: {data.target_industry}
Career Direction: {data.career_direction}
Experience Level: {data.experience_level}

Country Rules Engine:
{country_rules}

Resume Length Rules:
{length_rules}

Resume Style Engine:
{get_resume_style_models()}

Current Background:
{data.current_background}

Highest Qualification:
{data.highest_qualification}

Education Details:
{data.education_details}

Work Experience:
{data.work_experience}

Internships:
{data.internships}

Projects:
{data.projects}

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

Leadership Experience:
{data.leadership_experience}

Career Change:
{data.career_change}

Current Field:
{data.current_field}

Target Field:
{data.target_field}

Return ONLY valid JSON in this exact format:

{{
  "candidate_profile_type": "Student | Fresher | Early Career | Mid-Level | Senior | Executive",
  "career_direction_detected": "Technical | Non-Technical | Management | Sales | Marketing | Operations | Finance | Healthcare | Customer Support | Other",
  "career_change_detected": true,
  "recommended_resume_model": "Graduate ATS Resume | Technical Professional Resume | Career Switcher Resume | Business Professional Resume | Executive Leadership Resume",
  "resume_length_rule": "One Page | One to Two Pages | Two Pages",
  "target_market_strategy": "string",
  "recruiter_positioning": "string",
  "priority_sections": ["section1", "section2"],
  "sections_to_minimize_or_remove": ["section1", "section2"],
  "skill_grouping_strategy": [
    {{
      "category": "string",
      "skills": ["skill1", "skill2"]
    }}
  ],
  "ats_keyword_strategy": ["keyword1", "keyword2"],
  "missing_information": ["missing item 1", "missing item 2"],
  "content_risk_flags": ["risk1", "risk2"],
  "writing_guidance": "string"
}}

Rules:
1. Do not write the resume.
2. Do not create fake achievements.
3. Do not create fake metrics.
4. If experience level is Student, Fresher, or 1-5 years, recommend One Page unless there is strong reason otherwise.
5. If experience is 5-10 years, recommend One Page or One to Two Pages depending on content.
6. If experience is 10+ years, recommend Two Pages.
7. Never output labels like Template: India or Template: UK.
8. Use target country only to shape strategy, not as visible template label.
9. Group skills professionally.
10. Identify missing information that would improve the resume.
11. Identify sections that should be minimized.
12. For career changers, focus on transferable skills.
13. For technical roles, prioritize technical skills, projects, certifications, and relevant experience.
14. For non-technical roles, prioritize communication, operations, business tools, customer handling, leadership, coordination, reporting, and transferable skills.
15. Keep recruiter positioning specific and market-aware without writing the final resume.
"""

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.1,
    )

    content = (resp.choices[0].message.content or "").strip()
    parsed = parse_json_response(content)
    return normalize_resume_intelligence_result(parsed, data)


def build_resume_intelligence_request(data: ResumeIntelligenceInput) -> ResumeIntelligenceRequest:
    return ResumeIntelligenceRequest(
        target_role=data.target_role,
        target_country=data.target_country,
        target_industry=data.target_industry,
        career_direction=data.career_direction,
        experience_level=data.experience_level,
        current_background=data.current_background,
        highest_qualification=data.highest_qualification,
        education_details=data.education_details,
        work_experience=data.work_experience,
        internships=data.internships,
        projects=data.projects,
        technical_skills=data.technical_skills,
        transferable_skills=data.transferable_skills,
        tools_software=data.tools_software,
        certifications=data.certifications,
        achievements=data.achievements,
        leadership_experience=data.leadership_experience,
        career_change=data.career_change,
        current_field=data.current_field,
        target_field=data.target_field,
    )


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


@app.post("/analyze-resume-intelligence", response_model=ResumeIntelligenceAnalysisOutput)
def analyze_resume_intelligence(data: ResumeIntelligenceRequest):
    return generate_resume_intelligence(data)


@app.post("/optimize-resume", response_model=ResumeOptimizerOutput)
def optimize_resume(data: ResumeOptimizerInput):
    country_rules = get_country_rules(data.target_country)
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

Country Rules Engine:
{country_rules}

Resume Style Engine:
{get_resume_style_models()}

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
12. Group skills into logical clusters instead of listing them as a flat, repetitive skills block.
13. Keep length discipline appropriate to the likely seniority level suggested by the resume.

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

Resume length rules:
- Student / Fresher: maximum 1 page
- 1-5 years: 1 page
- 5-10 years: 1-2 pages
- 10+ years: 2 pages maximum
- Prioritize relevance and avoid repetition

ATS score estimate rules:
- Provide a short estimate like "High ATS readiness (82-88/100 range)" or "Moderate ATS readiness (68-75/100 range)"
- This is an internal estimate, not a guaranteed external ATS score

Return ONLY valid JSON in this exact format:
{{
  "recommended_resume_style": "string",
  "recommendation_reason": "string",
  "optimized_resume": "string",
  "ats_keywords": ["keyword1", "keyword2", "keyword3"],
  "strengths": ["strength1", "strength2"],
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
        "strengths",
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
    if not isinstance(parsed["strengths"], list):
        parsed["strengths"] = []
    if not isinstance(parsed["weaknesses_found"], list):
        parsed["weaknesses_found"] = []
    if not isinstance(parsed["improvement_suggestions"], list):
        parsed["improvement_suggestions"] = []

    parsed["ats_keywords"] = [str(x).strip() for x in parsed["ats_keywords"] if str(x).strip()]
    parsed["strengths"] = [str(x).strip() for x in parsed["strengths"] if str(x).strip()]
    parsed["weaknesses_found"] = [str(x).strip() for x in parsed["weaknesses_found"] if str(x).strip()]
    parsed["improvement_suggestions"] = [str(x).strip() for x in parsed["improvement_suggestions"] if str(x).strip()]
    return parsed


@app.post("/build-resume", response_model=ResumeBuildOutput)
def build_resume(data: ResumeIntelligenceInput):
    intelligence_request = build_resume_intelligence_request(data)
    intelligence = generate_resume_intelligence(intelligence_request)
    skill_intelligence = generate_skill_intelligence(data, intelligence)

    system_msg = (
        "You are a senior professional resume writer, ATS specialist, and career strategist with 15 years of experience. "
        "Your job is to create outstanding, recruiter-quality resumes that can compete with professional resume-writing services. "
        "You must follow the supplied resume intelligence strategy before writing. "
        "The final resume must be role-specific, country-aware, ATS-friendly, and aligned to the recommended resume model and length rule. "
        "Do not create generic AI summaries. "
        "Do not invent fake facts, employers, dates, degrees, certifications, metrics, achievements, or experience. "
        "If information is missing, omit the section from the resume or address it only in missing_information and improvement_suggestions. "
        "Never include placeholder text, template labels, test language, backend language, or preview language in the resume."
    )

    user_msg = f"""
Create a complete professional resume using the candidate information and the resume intelligence strategy below.

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

Resume Intelligence Analysis:
Recommended Resume Model: {intelligence['recommended_resume_model']}
Resume Length Rule: {intelligence['resume_length_rule']}
Target Market Strategy: {intelligence['target_market_strategy']}
Recruiter Positioning: {intelligence['recruiter_positioning']}
Priority Sections: {json.dumps(intelligence['priority_sections'])}
Sections To Minimize Or Remove: {json.dumps(intelligence['sections_to_minimize_or_remove'])}
Skill Grouping Strategy: {json.dumps(intelligence['skill_grouping_strategy'])}
Skill Intelligence Groups To Use Exactly: {json.dumps(skill_intelligence['skill_groups'])}
Priority Skills: {json.dumps(skill_intelligence['priority_skills'])}
Missing Role Skills: {json.dumps(skill_intelligence['missing_role_skills'])}
Skill Positioning Note: {skill_intelligence['skill_positioning_note']}
ATS Keyword Strategy: {json.dumps(intelligence['ats_keyword_strategy'])}
Missing Information To Keep Out Of Resume: {json.dumps(intelligence['missing_information'])}
Content Risk Flags: {json.dumps(intelligence['content_risk_flags'])}
Writing Guidance: {intelligence['writing_guidance']}

Writing Rules:
1. Follow the resume intelligence exactly.
2. If resume_length_rule is One Page, create a concise one-page style resume.
3. If the candidate has less than 10 years of experience, prioritize one-page structure unless content strongly justifies more.
4. Skills must always be grouped using the supplied skill intelligence groups exactly, never as one flat list.
5. Hide empty sections instead of showing placeholders.
6. Do not include placeholder text like [No formal work experience], [Details not provided], [No certifications provided], or [Year not provided].
7. Missing information should appear only in missing_information or improvement_suggestions, never inside the resume.
8. For freshers, prioritize education, projects, internships, skills, and certifications.
9. For career switchers, emphasize transferable skills and target-role relevance while minimizing irrelevant technical depth.
10. For senior candidates, emphasize leadership, business outcomes, operations ownership, team management, strategy, and measurable impact where supported.
11. If metrics are not provided, use impact-based language without fake numbers.
12. Never include Template labels, test, backend, or preview wording.
13. Use standard ATS-safe headings and clean formatting.
14. Professional Title must align with the target role and intelligence strategy.
15. If the user selected a specific preferred resume style instead of Auto Recommend, keep the final style aligned while still obeying the intelligence strategy.

Return ONLY valid JSON in this exact format:
{{
  "recommended_resume_style": "string",
  "recommendation_reason": "string",
  "professional_title": "string",
  "resume_length_rule": "string",
  "target_market_strategy": "string",
  "recruiter_positioning": "string",
  "full_resume": "string",
  "ats_keywords": ["keyword1", "keyword2"],
  "skill_groups": [
    {{
      "category": "string",
      "skills": ["skill1", "skill2"]
    }}
  ],
  "strengths": ["strength1", "strength2"],
  "missing_information": ["missing1", "missing2"],
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
        "resume_length_rule",
        "target_market_strategy",
        "recruiter_positioning",
        "full_resume",
        "ats_keywords",
        "skill_groups",
        "strengths",
        "missing_information",
        "improvement_suggestions",
    }

    if not required_keys.issubset(parsed.keys()):
        raise HTTPException(
            status_code=500,
            detail=f"Missing keys in resume builder response. Required: {required_keys}. Got: {list(parsed.keys())}",
        )

    parsed["recommended_resume_style"] = str(parsed.get("recommended_resume_style", "")).strip() or intelligence["recommended_resume_model"]
    parsed["recommendation_reason"] = str(parsed.get("recommendation_reason", "")).strip()
    parsed["professional_title"] = str(parsed.get("professional_title", "")).strip()
    parsed["resume_length_rule"] = str(parsed.get("resume_length_rule") or intelligence["resume_length_rule"]).strip() or intelligence["resume_length_rule"]
    parsed["target_market_strategy"] = str(parsed.get("target_market_strategy") or intelligence["target_market_strategy"]).strip() or intelligence["target_market_strategy"]
    parsed["recruiter_positioning"] = str(parsed.get("recruiter_positioning") or intelligence["recruiter_positioning"]).strip() or intelligence["recruiter_positioning"]
    parsed["full_resume"] = sanitize_resume_text(str(parsed.get("full_resume", "")).strip())
    parsed["ats_keywords"] = clean_string_list(parsed.get("ats_keywords", [])) or intelligence["ats_keyword_strategy"]
    parsed["skill_groups"] = clean_skill_groups(skill_intelligence["skill_groups"])
    parsed["strengths"] = clean_string_list(parsed.get("strengths", []))
    parsed["missing_information"] = clean_string_list(parsed.get("missing_information", [])) or intelligence["missing_information"]
    parsed["improvement_suggestions"] = clean_string_list(parsed.get("improvement_suggestions", []))

    if skill_intelligence["missing_role_skills"]:
        parsed["improvement_suggestions"].append(
            f"Consider building stronger exposure in: {', '.join(skill_intelligence['missing_role_skills'])}."
        )
        parsed["improvement_suggestions"] = clean_string_list(parsed["improvement_suggestions"])

    return parsed


@app.post("/review-resume", response_model=ResumeReviewerOutput)
def review_resume(data: ResumeReviewerInput):
    country_rules = get_country_rules(data.target_country)
    system_msg = (
        "You are a senior ATS optimization specialist, recruiter, and resume reviewer with 15 years of experience. "
        "Your job is to review an existing resume like a recruiter and ATS consultant would. "
        "You must identify what is working, what is weak, which keywords are missing, and why the ATS estimate was given. "
        "Do not invent facts from the resume. "
        "Do not use generic AI wording. "
        "Do not include template labels, preview, backend, or test language."
    )

    user_msg = f"""
Review this resume like a professional resume reviewer.

Target role: {data.target_role}
Target country / job market: {data.target_country}
Optional job description:
{data.job_description}

Country Rules Engine:
{country_rules}

Resume text:
{data.resume_text}

Tasks:
1. Estimate ATS readiness.
2. Explain clearly why that score estimate was given.
3. Identify missing keywords for the target role when possible.
4. Identify weak sections.
5. Identify strong sections.
6. Write recruiter feedback in a concise professional tone.
7. Give practical improvement suggestions.
8. Do not invent missing experiences, metrics, or employers.

ATS score format rules:
- Return ATS score in a professional estimate style such as "Low ATS readiness (30-40/100 range)" or "Moderate ATS readiness (60-70/100 range)"
- Do not return a raw percentage only

Return ONLY valid JSON in this exact format:
{{
  "ats_score_estimate": "string",
  "score_reason": "string",
  "missing_keywords": ["keyword1", "keyword2"],
  "weak_sections": ["section1", "section2"],
  "strong_sections": ["section1", "section2"],
  "recruiter_feedback": "string",
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
        "ats_score_estimate",
        "score_reason",
        "missing_keywords",
        "weak_sections",
        "strong_sections",
        "recruiter_feedback",
        "improvement_suggestions",
    }
    if not required_keys.issubset(parsed.keys()):
        raise HTTPException(
            status_code=500,
            detail=f"Missing keys in resume review response. Required: {required_keys}. Got: {list(parsed.keys())}",
        )

    for key in ("missing_keywords", "weak_sections", "strong_sections", "improvement_suggestions"):
        if not isinstance(parsed[key], list):
            parsed[key] = []
        parsed[key] = [str(x).strip() for x in parsed[key] if str(x).strip()]

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
