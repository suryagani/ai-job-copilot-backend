from __future__ import annotations


def _clean_list(values) -> list[str]:
    cleaned = []
    for value in values or []:
        text = str(value or "").strip()
        if text and text not in cleaned:
            cleaned.append(text)
    return cleaned


def review_cover_letter_quality(cover_letter_text, candidate_data, intelligence, job_intelligence, company_context, tone_config, client, parse_json_response):
    system_msg = (
        "You are a senior recruiter, cover letter reviewer, and ATS specialist. "
        "Evaluate the cover letter for role alignment, company alignment, tone, readability, and recruiter confidence. "
        "Do not reveal chain-of-thought. Return only structured JSON."
    )

    user_msg = f'''
Review this cover letter.

Target Role: {getattr(candidate_data, "target_role", "")}
Target Country: {getattr(candidate_data, "target_country", "")}
Company Name: {getattr(candidate_data, "company_name", "")}
Requested Tone: {tone_config.get("tone", "Professional")}
Recommended Resume Model: {intelligence.get("recommended_resume_model", "")}
Target Market Strategy: {intelligence.get("target_market_strategy", "")}
Job Description Intelligence: {job_intelligence or {}}
Company Context: {company_context}

Cover Letter:
{cover_letter_text}

Return ONLY valid JSON in this format:
{{
  "cover_letter_quality_score": 0,
  "ats_alignment_score": 0,
  "recruiter_confidence": 0,
  "issues_found": ["issue1"],
  "strengths_found": ["strength1"],
  "suggested_fixes": ["fix1"],
  "is_ready_for_user": true
}}

Rules:
1. Score all numeric values from 0 to 100.
2. Penalize generic openings, weak company alignment, or unsupported claims.
3. Penalize invented achievements or claims not grounded in the candidate context.
4. Reward clear value proposition, recruiter readability, and honest positioning.
'''

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.1,
    )
    parsed = parse_json_response((resp.choices[0].message.content or "").strip())
    parsed.setdefault("cover_letter_quality_score", 0)
    parsed.setdefault("ats_alignment_score", 0)
    parsed.setdefault("recruiter_confidence", 0)
    parsed["issues_found"] = _clean_list(parsed.get("issues_found", []))
    parsed["strengths_found"] = _clean_list(parsed.get("strengths_found", []))
    parsed["suggested_fixes"] = _clean_list(parsed.get("suggested_fixes", []))
    parsed["is_ready_for_user"] = bool(parsed.get("is_ready_for_user", False))
    for key in ["cover_letter_quality_score", "ats_alignment_score", "recruiter_confidence"]:
        try:
            parsed[key] = max(0, min(100, int(parsed.get(key, 0))))
        except Exception:
            parsed[key] = 0
    return parsed
