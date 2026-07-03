from __future__ import annotations


def recommend_featured_section(candidate_data, achievement_intelligence: dict | None = None, career_knowledge: dict | None = None) -> list[str]:
    featured = []
    portfolio = str(getattr(candidate_data, "portfolio_url", "") or "").strip()
    linkedin = str(getattr(candidate_data, "linkedin_url", "") or "").strip()
    certifications = str(getattr(candidate_data, "certifications", "") or "").strip()
    projects = str(getattr(candidate_data, "projects", "") or "").strip()
    if portfolio:
        featured.append(f"Portfolio / GitHub: {portfolio}")
    if projects:
        featured.append("Pin 1-2 strongest project case studies with problem, approach, and result.")
    if certifications:
        featured.append("Add the most relevant certification or workshop proof to Featured.")
    if linkedin:
        featured.append("Publish one short post highlighting a project or career insight and pin it in Featured.")
    if not featured:
        featured.append("Add a project showcase, certificate, or short insight post to strengthen your Featured section.")
    if career_knowledge and career_knowledge.get("recommended_projects"):
        featured.append(f"Suggested portfolio angle: {career_knowledge['recommended_projects'][0]}")
    return featured[:5]
