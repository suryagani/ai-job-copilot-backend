from __future__ import annotations

COMPANY_EXPECTATIONS = {
    'Startup': ['ownership', 'adaptability', 'execution speed'],
    'Enterprise': ['process discipline', 'collaboration', 'scalability'],
    'Government': ['reliability', 'communication', 'procedural clarity'],
    'Consultancy': ['client communication', 'problem solving', 'presentation'],
    'Product Company': ['product thinking', 'delivery quality', 'cross-functional work'],
    'Research': ['analysis', 'experimentation', 'structured thinking'],
    'Manufacturing': ['operations discipline', 'quality', 'process improvement'],
    'Healthcare': ['accuracy', 'trust', 'documentation'],
    'Retail': ['customer focus', 'coordination', 'execution'],
    'Hospitality': ['service reliability', 'leadership', 'customer handling'],
    'General': ['clarity', 'professionalism', 'role fit'],
}


def infer_company_type(company_name: str = '', industry: str = '', job_intelligence: dict | None = None) -> str:
    if job_intelligence and job_intelligence.get('company_type_guess'):
        return str(job_intelligence['company_type_guess']).strip() or 'General'
    haystack = f"{company_name} {industry}".lower()
    if any(token in haystack for token in ['hospitality', 'restaurant', 'hotel', 'cafe']):
        return 'Hospitality'
    if any(token in haystack for token in ['consult', 'advisory', 'services']):
        return 'Consultancy'
    if any(token in haystack for token in ['lab', 'research', 'institute']):
        return 'Research'
    if any(token in haystack for token in ['tech', 'software', 'platform', 'product']):
        return 'Product Company'
    return 'General'


def build_company_context(company_name: str = '', target_role: str = '', target_country: str = 'Global', industry: str = '', job_intelligence: dict | None = None) -> dict:
    company_type = infer_company_type(company_name, industry, job_intelligence)
    expectations = COMPANY_EXPECTATIONS.get(company_type, COMPANY_EXPECTATIONS['General'])
    name = (company_name or '').strip() or 'the company'
    return {
        'company_name': name,
        'company_type': company_type,
        'interview_expectations': expectations,
        'company_interview_note': f"Prepare for {name} with emphasis on {', '.join(expectations[:3])} for the {target_role or 'target'} role in {target_country}.",
    }
