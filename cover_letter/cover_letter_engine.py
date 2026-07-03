from __future__ import annotations

from .company_research import build_company_context
from .cover_letter_quality import review_cover_letter_quality
from .cover_letter_renderer import render_cover_letter_package
from .cover_letter_templates import build_greeting, build_signature, get_template_config

PROHIBITED_LABELS = ["Template:", "backend", "preview", "test"]


def _clean_list(values) -> list[str]:
    cleaned = []
    for value in values or []:
        text = str(value or "").strip()
        if text and text not in cleaned:
            cleaned.append(text)
    return cleaned


def _sanitize_cover_letter(text: str) -> str:
    output = str(text or "").strip()
    for label in PROHIBITED_LABELS:
        output = output.replace(label, "")
    return "\n".join(line.rstrip() for line in output.splitlines()).strip()


def _format_skill_groups(skill_intelligence: dict | None) -> str:
    groups = []
    for group in (skill_intelligence or {}).get("skill_groups", []):
        category = str(group.get("category", "")).strip()
        skills = ", ".join(_clean_list(group.get("skills", [])))
        if category and skills:
            groups.append(f"{category}: {skills}")
    return "\n".join(groups)


def _build_candidate_snapshot(candidate_data, achievement_intelligence: dict | None) -> str:
    achievements = []
    for item in (achievement_intelligence or {}).get("experience_bullets", [])[:3]:
        improved = str(item.get("improved", "")).strip()
        if improved:
            achievements.append(f"- {improved}")
    for project in (achievement_intelligence or {}).get("project_bullets", [])[:2]:
        for bullet in project.get("improved_bullets", [])[:2]:
            text = str(bullet or "").strip()
            if text:
                achievements.append(f"- {text}")
    parts = [
        f"Current background: {getattr(candidate_data, 'current_background', '')}",
        f"Work experience: {getattr(candidate_data, 'work_experience', '')}",
        f"Internships: {getattr(candidate_data, 'internships', '')}",
        f"Projects: {getattr(candidate_data, 'projects', '')}",
        "Achievement bullets:",
        "\n".join(achievements),
    ]
    return "\n".join(part for part in parts if str(part).strip())


def _build_prompt(candidate_data, intelligence, skill_intelligence, achievement_intelligence, job_intelligence, recruiter_intelligence, ats_intelligence, personalization, career_knowledge, resume_model_name, tone_config, company_context, greeting, signature, rewrite_context=None):
    rewrite_context = rewrite_context or {}
    return f'''
Write a recruiter-quality cover letter using only verified candidate information.

Candidate Details:
Full Name: {getattr(candidate_data, "full_name", "")}
Email: {getattr(candidate_data, "email", "")}
Phone: {getattr(candidate_data, "phone", "")}
Location: {getattr(candidate_data, "location", "")}
LinkedIn: {getattr(candidate_data, "linkedin_url", "")}
Portfolio: {getattr(candidate_data, "portfolio_url", "")}

Target Strategy:
Target Role: {getattr(candidate_data, "target_role", "")}
Target Country: {getattr(candidate_data, "target_country", "")}
Target Industry: {getattr(candidate_data, "target_industry", "")}
Experience Level: {getattr(candidate_data, "experience_level", "")}
Years of Experience: {getattr(candidate_data, "years_of_experience", "") or getattr(candidate_data, "experience_level", "")}
Requested Tone: {tone_config.get("tone", "Professional")}
Resume Model Guidance: {resume_model_name}

Greeting: {greeting}
Signature: {signature}

Resume Intelligence:
{intelligence}

Skill Intelligence:
{_format_skill_groups(skill_intelligence)}

Achievement Intelligence Snapshot:
{_build_candidate_snapshot(candidate_data, achievement_intelligence)}

Job Description Intelligence:
{job_intelligence or {}}

Recruiter Intelligence:
{recruiter_intelligence or {}}

ATS Intelligence:
{ats_intelligence or {}}

Resume Personalization:
{personalization or {}}

Career Knowledge Graph Context:
{career_knowledge or {}}

Company Context:
{company_context}

Optional Job Description:
{getattr(candidate_data, "job_description", "")}

Optional Rewrite Context:
{rewrite_context}

Required structure:
1. Professional Header
2. Greeting
3. Opening Paragraph
4. Candidate Value Proposition
5. Relevant Experience
6. Projects / Achievements
7. Why This Company
8. Closing Paragraph
9. Professional Signature

Rules:
1. Never invent experience, projects, metrics, employers, achievements, or certifications.
2. If company details are limited, stay respectful and avoid unsupported claims.
3. Sound like an experienced recruiter or career consultant wrote it.
4. Keep it concise, polished, and ATS-friendly.
5. Make the candidate's value clear within the first paragraph.
6. Use the requested tone guidance: {tone_config}.
7. Do not include labels like Template, backend, preview, or test.

Return ONLY valid JSON in this format:
{{
  "cover_letter_text": "string",
  "opening_strategy": "string",
  "company_alignment_note": "string",
  "closing_positioning": "string"
}}
'''


def generate_cover_letter_package(candidate_data, intelligence, skill_intelligence, achievement_intelligence, job_intelligence, recruiter_intelligence, ats_intelligence, personalization, career_knowledge, resume_model_name, client, parse_json_response):
    tone_config = get_template_config(getattr(candidate_data, "tone", "Professional"), getattr(candidate_data, "experience_level", ""))
    company_context = build_company_context(
        company_name=getattr(candidate_data, "company_name", ""),
        target_country=getattr(candidate_data, "target_country", "Global"),
        target_role=getattr(candidate_data, "target_role", ""),
        target_industry=getattr(candidate_data, "target_industry", ""),
        job_intelligence=job_intelligence,
    )
    greeting = build_greeting(getattr(candidate_data, "hiring_manager", ""))
    signature = build_signature(getattr(candidate_data, "full_name", ""))

    system_msg = (
        "You are a senior recruiter, ATS specialist, and cover letter consultant with 15 years of experience. "
        "Write natural, role-aware, company-aware cover letters that sound human, premium, and truthful. "
        "Do not invent facts. Do not use generic AI phrasing. Return only valid JSON."
    )

    user_msg = _build_prompt(
        candidate_data,
        intelligence,
        skill_intelligence,
        achievement_intelligence,
        job_intelligence,
        recruiter_intelligence,
        ats_intelligence,
        personalization,
        career_knowledge,
        resume_model_name,
        tone_config,
        company_context,
        greeting,
        signature,
    )

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.3,
    )
    parsed = parse_json_response((resp.choices[0].message.content or "").strip())
    cover_letter_text = _sanitize_cover_letter(parsed.get("cover_letter_text", ""))

    quality = review_cover_letter_quality(
        cover_letter_text,
        candidate_data,
        intelligence,
        job_intelligence,
        company_context,
        tone_config,
        client,
        parse_json_response,
    )

    if (not quality.get("is_ready_for_user", False)) or quality.get("cover_letter_quality_score", 0) < 80:
        rewrite_context = {
            "issues_found": quality.get("issues_found", []),
            "suggested_fixes": quality.get("suggested_fixes", []),
            "previous_draft": cover_letter_text,
        }
        resp = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": _build_prompt(candidate_data, intelligence, skill_intelligence, achievement_intelligence, job_intelligence, recruiter_intelligence, ats_intelligence, personalization, career_knowledge, resume_model_name, tone_config, company_context, greeting, signature, rewrite_context=rewrite_context)},
            ],
            temperature=0.25,
        )
        parsed = parse_json_response((resp.choices[0].message.content or "").strip())
        cover_letter_text = _sanitize_cover_letter(parsed.get("cover_letter_text", ""))
        quality = review_cover_letter_quality(
            cover_letter_text,
            candidate_data,
            intelligence,
            job_intelligence,
            company_context,
            tone_config,
            client,
            parse_json_response,
        )

    rendered = render_cover_letter_package(
        full_name=getattr(candidate_data, "full_name", ""),
        target_role=getattr(candidate_data, "target_role", ""),
        company_name=getattr(candidate_data, "company_name", ""),
        cover_letter_text=cover_letter_text,
        target_country=getattr(candidate_data, "target_country", "Global"),
    )

    return {
        "cover_letter_text": cover_letter_text,
        "cover_letter_pdf_path": rendered["cover_letter_pdf_path"],
        "cover_letter_docx_path": rendered["cover_letter_docx_path"],
        "cover_letter_quality_score": quality.get("cover_letter_quality_score", 0),
        "ats_alignment_score": quality.get("ats_alignment_score", 0),
        "recruiter_confidence": quality.get("recruiter_confidence", 0),
    }
