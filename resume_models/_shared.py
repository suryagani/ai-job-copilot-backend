import json

from .runtime import get_runtime


def _render_context(candidate_data, intelligence, skill_intelligence, achievement_intelligence, ats_intelligence, recruiter_intelligence, job_intelligence, personalization):
    return f"""
Candidate Details:
Full Name: {getattr(candidate_data, 'full_name', '')}
Email: {getattr(candidate_data, 'email', '')}
Phone: {getattr(candidate_data, 'phone', '')}
Location: {getattr(candidate_data, 'location', '')}
LinkedIn: {getattr(candidate_data, 'linkedin_url', '')}
Portfolio/GitHub: {getattr(candidate_data, 'portfolio_url', '')}

Target Strategy:
Target Role: {getattr(candidate_data, 'target_role', '')}
Target Country: {getattr(candidate_data, 'target_country', '')}
Target Industry: {getattr(candidate_data, 'target_industry', '')}
Career Direction: {getattr(candidate_data, 'career_direction', '')}
Experience Level: {getattr(candidate_data, 'experience_level', '')}

Background:
Current Background: {getattr(candidate_data, 'current_background', '')}
Highest Qualification: {getattr(candidate_data, 'highest_qualification', '')}
Education Details:
{getattr(candidate_data, 'education_details', '')}

Work Experience:
{getattr(candidate_data, 'work_experience', '')}

Internships:
{getattr(candidate_data, 'internships', '')}

Projects:
{getattr(candidate_data, 'projects', '')}

Technical Skills:
{getattr(candidate_data, 'technical_skills', '')}

Transferable Skills:
{getattr(candidate_data, 'transferable_skills', '')}

Tools / Software:
{getattr(candidate_data, 'tools_software', '')}

Certifications:
{getattr(candidate_data, 'certifications', '')}

Achievements:
{getattr(candidate_data, 'achievements', '')}

Leadership / Team Experience:
{getattr(candidate_data, 'leadership_experience', '')}

Career Change:
Career Change: {getattr(candidate_data, 'career_change', '')}
Current Field: {getattr(candidate_data, 'current_field', '')}
Target Field: {getattr(candidate_data, 'target_field', '')}

Resume Intelligence:
{json.dumps(intelligence)}

Skill Intelligence:
{json.dumps(skill_intelligence)}

Achievement Intelligence:
{json.dumps(achievement_intelligence)}

ATS Intelligence:
{json.dumps(ats_intelligence)}

Recruiter Intelligence:
{json.dumps(recruiter_intelligence or {})}

Job Intelligence:
{json.dumps(job_intelligence or {})}

Resume Personalization:
{json.dumps(personalization or {})}
"""


def generate_resume_with_strategy(model_name, model_instructions, candidate_data, intelligence, skill_intelligence, achievement_intelligence, ats_intelligence, recruiter_intelligence, job_intelligence, personalization):
    client, parser = get_runtime()

    rewrite_context = intelligence.get("rewrite_context", {})
    rewrite_block = ""
    if rewrite_context:
        rewrite_block = f"""
Rewrite Context:
First Draft Resume:
{rewrite_context.get('draft_resume', '')}

First Draft Summary:
{rewrite_context.get('draft_summary', '')}

Quality Issues:
{json.dumps(rewrite_context.get('issues_found', []))}

Required Fixes:
{json.dumps(rewrite_context.get('required_fixes', []))}

Rewrite Instructions:
- Fix every listed issue.
- Keep the model-specific section order and writing style.
- Preserve grouped skills and truthful achievement bullets.
- Remove any weak or repetitive wording.
"""

    system_msg = (
        "You are a premium resume-writing engine. "
        "Write naturally, professionally, and truthfully. "
        "Do not invent employers, dates, achievements, metrics, projects, certifications, or skills. "
        "Do not use generic AI wording. "
        "Return only valid JSON."
    )

    user_msg = f"""
Selected Resume Writing Model: {model_name}

Model Instructions:
{model_instructions}

Core Rules:
- Follow the selected writing model exactly.
- Use ATS-safe headings and clean formatting.
- Skills must reflect grouped skills from Skill Intelligence.
- Use Achievement Intelligence to strengthen bullets truthfully.
- Use ATS Intelligence to place matching keywords naturally without keyword stuffing.
- Use Resume Personalization to adapt tone, emphasis, and order.
- Use Job Intelligence only to sharpen truthful alignment.
- Hide empty sections completely.
- Do not use placeholders such as [Current Employer], [Dates], [Institution], [Company], N/A, or Not Provided.
- Keep the resume aligned to the recommended length rule.

Return ONLY valid JSON in this exact format:
{{
  "professional_title": "string",
  "summary": "string",
  "section_order": ["section1", "section2"],
  "resume": "string"
}}

{_render_context(candidate_data, intelligence, skill_intelligence, achievement_intelligence, ats_intelligence, recruiter_intelligence, job_intelligence, personalization)}
{rewrite_block}
"""

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.15,
    )
    content = (resp.choices[0].message.content or "").strip()
    parsed = parser(content)

    required = {"professional_title", "summary", "section_order", "resume"}
    if not required.issubset(parsed.keys()):
        raise ValueError(f"Missing resume model keys. Required: {required}. Got: {list(parsed.keys())}")

    if not isinstance(parsed["section_order"], list):
        parsed["section_order"] = []

    return {
        "professional_title": str(parsed.get("professional_title", "")).strip(),
        "summary": str(parsed.get("summary", "")).strip(),
        "section_order": [str(item).strip() for item in parsed.get("section_order", []) if str(item).strip()],
        "resume": str(parsed.get("resume", "")).strip(),
    }
