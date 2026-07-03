from __future__ import annotations


def _clean_list(values) -> list[str]:
    cleaned = []
    for value in values or []:
        text = str(value or "").strip()
        if text and text not in cleaned:
            cleaned.append(text)
    return cleaned


def review_linkedin_profile(output: dict, candidate_data, contexts: dict, client, parse_json_response) -> dict:
    system_msg = (
        "You are a senior LinkedIn branding expert, recruiter, and visibility strategist. "
        "Evaluate the profile for recruiter discoverability, keyword alignment, professionalism, clarity, and authenticity. "
        "Return only structured JSON."
    )
    user_msg = f'''\nReview this LinkedIn optimization output.\n\nTarget Role: {getattr(candidate_data, "target_role", "")}\nTarget Country: {getattr(candidate_data, "target_country", "")}\nTarget Industry: {getattr(candidate_data, "target_industry", "")}\nContexts:\n{contexts}\n\nOutput:\n{output}\n\nReturn ONLY valid JSON in this format:\n{{\n  "headline_score": 0,\n  "linkedin_score": 0,\n  "recruiter_visibility_score": 0,\n  "quality_notes": ["note1"],\n  "visibility_explanation": "string",\n  "suggested_fixes": ["fix1"],\n  "is_ready_for_user": true\n}}\n'''
    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.1,
    )
    parsed = parse_json_response((resp.choices[0].message.content or "").strip())
    for key in ["headline_score", "linkedin_score", "recruiter_visibility_score"]:
        try:
            parsed[key] = max(0, min(100, int(parsed.get(key, 0))))
        except Exception:
            parsed[key] = 0
    parsed["quality_notes"] = _clean_list(parsed.get("quality_notes", []))
    parsed["suggested_fixes"] = _clean_list(parsed.get("suggested_fixes", []))
    parsed["visibility_explanation"] = str(parsed.get("visibility_explanation", "")).strip()
    parsed["is_ready_for_user"] = bool(parsed.get("is_ready_for_user", False))
    return parsed
