from __future__ import annotations

COMPANY_TYPE_SIGNALS = {
    "Startup": ["startup", "labs", "ventures", "innovation", "studio"],
    "Enterprise": ["global", "enterprise", "group", "corporation", "corp", "technologies"],
    "Government": ["government", "ministry", "public", "authority", "municipal"],
    "Consultancy": ["consulting", "advisory", "services", "solutions"],
    "Product Company": ["product", "platform", "software", "systems"],
    "Research": ["research", "institute", "laboratory", "lab"],
    "Manufacturing": ["manufacturing", "industries", "industrial", "factory"],
    "Healthcare": ["health", "medical", "clinic", "hospital", "pharma"],
    "Retail": ["retail", "store", "commerce", "mart"],
    "Hospitality": ["hotel", "restaurant", "hospitality", "cafe"],
}

COMPANY_PRIORITIES = {
    "Startup": ["ownership", "adaptability", "problem solving", "delivery pace"],
    "Enterprise": ["process discipline", "collaboration", "scalability", "documentation"],
    "Government": ["reliability", "compliance", "communication", "procedural consistency"],
    "Consultancy": ["client service", "communication", "analysis", "presentation"],
    "Product Company": ["product thinking", "execution quality", "user impact", "cross-functional work"],
    "Research": ["analysis", "experimentation", "documentation", "structured thinking"],
    "Manufacturing": ["operations discipline", "quality", "process improvement", "coordination"],
    "Healthcare": ["accuracy", "care standards", "documentation", "stakeholder trust"],
    "Retail": ["customer focus", "operations", "inventory awareness", "team coordination"],
    "Hospitality": ["customer experience", "operations", "leadership", "service reliability"],
    "General": ["relevance", "professionalism", "clarity", "role alignment"],
}

COUNTRY_STYLE = {
    "usa": "achievement-led and direct",
    "canada": "balanced, clear, and evidence-aware",
    "uk": "concise, professional, and understated",
    "australia": "evidence-based, practical, and grounded",
    "germany": "structured, precise, and formal",
    "uae": "leadership-aware, polished, and operationally confident",
    "india": "skills-forward, practical, and recruiter-friendly",
}


def infer_company_type(company_name: str = "", target_industry: str = "", company_type_guess: str = "") -> str:
    explicit = (company_type_guess or "").strip()
    if explicit:
        return explicit
    haystack = f"{company_name} {target_industry}".lower()
    for label, keywords in COMPANY_TYPE_SIGNALS.items():
        if any(keyword in haystack for keyword in keywords):
            return label
    return "General"


def build_company_context(company_name: str = "", target_country: str = "Global", target_role: str = "", target_industry: str = "", job_intelligence: dict | None = None) -> dict:
    job_intelligence = job_intelligence or {}
    company_type = infer_company_type(company_name, target_industry, job_intelligence.get("company_type_guess", ""))
    country_style = COUNTRY_STYLE.get((target_country or "").strip().lower(), "professional and ATS-aware")
    priorities = COMPANY_PRIORITIES.get(company_type, COMPANY_PRIORITIES["General"])
    display_name = (company_name or "").strip() or "the organisation"
    company_alignment = (
        f"Position the candidate for {display_name} using a {country_style} tone, with emphasis on "
        f"{', '.join(priorities[:3])} for the target role of {target_role or 'the opportunity'}."
    )
    return {
        "company_name": display_name,
        "company_type": company_type,
        "country_style": country_style,
        "employer_priorities": priorities,
        "company_alignment_note": company_alignment,
        "research_confidence": "High" if company_name else "Medium",
    }
