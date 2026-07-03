from __future__ import annotations


def _clean_list(values) -> list[str]:
    cleaned = []
    for value in values or []:
        text = str(value or '').strip()
        if text and text not in cleaned:
            cleaned.append(text)
    return cleaned


def review_portfolio(content: dict, candidate_data, contexts: dict, client, parse_json_response) -> dict:
    system_msg = (
        'You are a senior portfolio strategist, recruiter, SEO reviewer, and hiring manager. '
        'Evaluate the portfolio output for professionalism, recruiter impression, SEO clarity, and project readability. '
        'Return only structured JSON.'
    )
    user_msg = f'''\nReview this portfolio output.\n\nTarget Role: {getattr(candidate_data, "target_role", "")}\nTarget Country: {getattr(candidate_data, "target_country", "")}\nTarget Industry: {getattr(candidate_data, "target_industry", "")}\nContexts:\n{contexts}\n\nPortfolio Content:\n{content}\n\nReturn ONLY valid JSON in this format:\n{{\n  "portfolio_score": 0,\n  "recruiter_score": 0,\n  "quality_notes": ["note1"],\n  "suggested_fixes": ["fix1"],\n  "is_ready_for_user": true\n}}\n'''
    resp = client.chat.completions.create(
        model='gpt-4.1-mini',
        messages=[
            {'role': 'system', 'content': system_msg},
            {'role': 'user', 'content': user_msg},
        ],
        temperature=0.1,
    )
    parsed = parse_json_response((resp.choices[0].message.content or '').strip())
    for key in ['portfolio_score', 'recruiter_score']:
        try:
            parsed[key] = max(0, min(100, int(parsed.get(key, 0))))
        except Exception:
            parsed[key] = 0
    parsed['quality_notes'] = _clean_list(parsed.get('quality_notes', []))
    parsed['suggested_fixes'] = _clean_list(parsed.get('suggested_fixes', []))
    parsed['is_ready_for_user'] = bool(parsed.get('is_ready_for_user', False))
    return parsed
