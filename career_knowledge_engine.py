from typing import Any


DEGREE_PATHWAYS: dict[str, dict[str, Any]] = {
    "ece": {
        "aliases": ["ece", "electronics and communication", "electronics & communication", "electronics engineering"],
        "roles": [
            "Physical Design Engineer",
            "VLSI Engineer",
            "Embedded Engineer",
            "FPGA Engineer",
            "Hardware Validation Engineer",
            "Telecommunications Engineer",
            "QA Engineer",
            "DevOps Engineer",
            "Business Analyst",
            "Operations Analyst",
        ],
        "industries": ["Semiconductor", "Embedded Systems", "Telecommunications", "Electronics Manufacturing"],
    },
    "computer_science": {
        "aliases": ["computer science", "cse", "software engineering", "information technology", "it"],
        "roles": [
            "Software Engineer",
            "Backend Engineer",
            "Frontend Engineer",
            "Full Stack Engineer",
            "DevOps Engineer",
            "Cloud Engineer",
            "AI Engineer",
            "Data Engineer",
            "Cybersecurity Engineer",
            "QA Engineer",
        ],
        "industries": ["Software", "Cloud", "SaaS", "Data", "Cybersecurity"],
    },
    "mechanical": {
        "aliases": ["mechanical", "mechanical engineering"],
        "roles": [
            "Mechanical Engineer",
            "Manufacturing Engineer",
            "Production Engineer",
            "Quality Engineer",
            "Operations Engineer",
            "Maintenance Engineer",
        ],
        "industries": ["Manufacturing", "Automotive", "Industrial Engineering"],
    },
    "civil": {
        "aliases": ["civil", "civil engineering", "structural engineering"],
        "roles": [
            "Civil Engineer",
            "Structural Engineer",
            "Site Engineer",
            "Construction Engineer",
            "Project Engineer",
            "Quantity Surveyor",
        ],
        "industries": ["Construction", "Infrastructure", "Real Estate"],
    },
    "commerce_business": {
        "aliases": ["commerce", "bcom", "business administration", "bba", "mba", "management"],
        "roles": [
            "Business Analyst",
            "Operations Analyst",
            "Sales Executive",
            "Marketing Executive",
            "HR Executive",
            "Account Executive",
            "Finance Analyst",
        ],
        "industries": ["Business Services", "Operations", "Sales", "Marketing", "Finance"],
    },
    "hospitality": {
        "aliases": ["chef", "culinary", "hotel management", "hospitality", "restaurant"],
        "roles": [
            "Restaurant Manager",
            "Operations Manager",
            "Kitchen Supervisor",
            "Food Production Manager",
            "Hospitality Manager",
            "Customer Experience Manager",
        ],
        "industries": ["Hospitality", "Food Service", "Retail Operations"],
    },
    "logistics": {
        "aliases": ["warehouse", "logistics", "supply chain", "inventory", "shipping"],
        "roles": [
            "Operations Coordinator",
            "Logistics Manager",
            "Supply Chain Analyst",
            "Inventory Controller",
            "Warehouse Operations Manager",
            "Procurement Coordinator",
        ],
        "industries": ["Logistics", "Supply Chain", "Warehousing", "Distribution"],
    },
}


ROLE_PROFILES: dict[str, dict[str, Any]] = {
    "physical design engineer": {
        "skills": ["Linux", "Physical Design Flow", "Timing Analysis", "ICC", "STA", "RTL", "SoC"],
        "ats_keywords": ["Physical Design", "Timing Analysis", "STA", "RTL", "Floorplanning", "Linux"],
        "certifications": ["VLSI Design", "ASIC Physical Design", "Linux Administration Basics"],
        "projects": ["ASIC physical design flow simulation", "Timing analysis case study", "RTL-to-GDS flow project"],
        "industries": ["Semiconductor"],
        "resume_model": "Technical Professional Resume",
        "growth_roles": ["Senior Physical Design Engineer", "ASIC Design Engineer", "VLSI Lead"],
        "company_types": ["Product Company", "Enterprise", "Research", "Manufacturing"],
    },
    "vlsi engineer": {
        "skills": ["VLSI Basics", "Linux", "Verilog", "Timing Analysis", "Verification Support", "RTL"],
        "ats_keywords": ["VLSI", "RTL", "Verification", "Physical Design", "Linux", "Digital Design"],
        "certifications": ["VLSI Design", "Digital IC Design"],
        "projects": ["Digital design mini project", "Verification support project", "FPGA implementation project"],
        "industries": ["Semiconductor", "Electronics"],
        "resume_model": "Graduate ATS Resume",
        "growth_roles": ["Senior VLSI Engineer", "Design Verification Engineer", "FPGA Engineer"],
        "company_types": ["Product Company", "Research", "Manufacturing"],
    },
    "embedded engineer": {
        "skills": ["Embedded C", "Microcontrollers", "Linux", "Firmware Debugging", "Serial Communication"],
        "ats_keywords": ["Embedded Systems", "Firmware", "Microcontrollers", "C Programming", "Linux"],
        "certifications": ["Embedded Systems", "IoT Foundations"],
        "projects": ["Microcontroller automation project", "Embedded firmware prototype", "Sensor integration project"],
        "industries": ["Embedded Systems", "Automotive", "Electronics"],
        "resume_model": "Technical Professional Resume",
        "growth_roles": ["Senior Embedded Engineer", "Firmware Engineer", "Hardware Systems Engineer"],
        "company_types": ["Product Company", "Manufacturing", "Research"],
    },
    "fpga engineer": {
        "skills": ["Verilog", "VHDL", "FPGA", "ModelSim", "Timing Analysis", "Digital Design"],
        "ats_keywords": ["FPGA", "Verilog", "Simulation", "Timing Analysis", "RTL Design"],
        "certifications": ["FPGA Design", "Digital Systems"],
        "projects": ["FPGA-based controller", "RTL simulation project", "Digital signal processing design"],
        "industries": ["Semiconductor", "Embedded Systems"],
        "resume_model": "Technical Professional Resume",
        "growth_roles": ["Senior FPGA Engineer", "RTL Design Engineer", "Hardware Validation Engineer"],
        "company_types": ["Product Company", "Research", "Manufacturing"],
    },
    "software engineer": {
        "skills": ["Python", "Java", "JavaScript", "Git", "Problem Solving", "APIs"],
        "ats_keywords": ["Software Development", "Backend", "Frontend", "APIs", "Version Control"],
        "certifications": ["Software Engineering", "Python", "Cloud Fundamentals"],
        "projects": ["Web application", "API service", "Automation tool"],
        "industries": ["Software", "SaaS", "Product"],
        "resume_model": "Technical Professional Resume",
        "growth_roles": ["Senior Software Engineer", "Tech Lead", "Engineering Manager"],
        "company_types": ["Startup", "Enterprise", "Product Company", "Consultancy"],
    },
    "backend engineer": {
        "skills": ["Python", "Java", "Node.js", "SQL", "APIs", "System Design"],
        "ats_keywords": ["Backend", "APIs", "Databases", "Scalability", "Microservices"],
        "certifications": ["Backend Development", "Cloud Fundamentals"],
        "projects": ["REST API platform", "Database-backed application", "Authentication service"],
        "industries": ["Software", "SaaS", "Fintech"],
        "resume_model": "Technical Professional Resume",
        "growth_roles": ["Senior Backend Engineer", "Platform Engineer", "Technical Architect"],
        "company_types": ["Startup", "Enterprise", "Product Company"],
    },
    "frontend engineer": {
        "skills": ["JavaScript", "React", "HTML", "CSS", "UI Development", "Responsive Design"],
        "ats_keywords": ["Frontend", "React", "JavaScript", "UI", "Responsive Design"],
        "certifications": ["Frontend Development", "JavaScript"],
        "projects": ["Responsive web app", "Dashboard UI", "Design system implementation"],
        "industries": ["Software", "SaaS", "Product"],
        "resume_model": "Technical Professional Resume",
        "growth_roles": ["Senior Frontend Engineer", "UI Engineer", "Frontend Lead"],
        "company_types": ["Startup", "Product Company", "Consultancy"],
    },
    "devops engineer": {
        "skills": ["AWS", "Docker", "Jenkins", "Linux", "CI/CD", "Terraform", "Monitoring"],
        "ats_keywords": ["DevOps", "CI/CD", "Docker", "AWS", "Linux", "Automation"],
        "certifications": ["AWS", "Docker", "Kubernetes", "Terraform"],
        "projects": ["CI/CD pipeline automation", "Cloud deployment project", "Infrastructure as code setup"],
        "industries": ["Cloud", "SaaS", "Software"],
        "resume_model": "Technical Professional Resume",
        "growth_roles": ["Senior DevOps Engineer", "Platform Engineer", "Cloud Architect"],
        "company_types": ["Startup", "Enterprise", "Product Company", "Consultancy"],
    },
    "cloud engineer": {
        "skills": ["AWS", "Azure", "Linux", "Networking", "Infrastructure", "Automation"],
        "ats_keywords": ["Cloud", "Infrastructure", "AWS", "Azure", "Automation", "Monitoring"],
        "certifications": ["AWS", "Azure", "Cloud Architect"],
        "projects": ["Cloud migration project", "Infrastructure automation", "Monitoring stack setup"],
        "industries": ["Cloud", "SaaS", "Enterprise Technology"],
        "resume_model": "Technical Professional Resume",
        "growth_roles": ["Senior Cloud Engineer", "Cloud Architect", "Platform Lead"],
        "company_types": ["Enterprise", "Product Company", "Consultancy"],
    },
    "business analyst": {
        "skills": ["Excel", "SQL", "Documentation", "Requirements Gathering", "Stakeholder Management", "Reporting"],
        "ats_keywords": ["Business Analysis", "Documentation", "Requirements", "Stakeholders", "Reporting"],
        "certifications": ["Business Analysis", "Power BI", "SQL"],
        "projects": ["Process mapping case study", "Dashboard reporting project", "Requirements documentation sample"],
        "industries": ["Business Services", "Operations", "Analytics", "Consulting"],
        "resume_model": "Business Professional Resume",
        "growth_roles": ["Senior Business Analyst", "Product Analyst", "Operations Manager"],
        "company_types": ["Enterprise", "Consultancy", "Product Company", "Government"],
    },
    "operations analyst": {
        "skills": ["Excel", "Reporting", "Process Improvement", "Coordination", "Data Analysis"],
        "ats_keywords": ["Operations", "Process Improvement", "Reporting", "Coordination", "Analysis"],
        "certifications": ["Operations Management", "Excel", "Lean Six Sigma"],
        "projects": ["Operations dashboard", "Process improvement case study", "Inventory/reporting workflow"],
        "industries": ["Operations", "Logistics", "Retail", "Business Services"],
        "resume_model": "Business Professional Resume",
        "growth_roles": ["Operations Manager", "Process Analyst", "Supply Chain Analyst"],
        "company_types": ["Enterprise", "Startup", "Retail", "Hospitality"],
    },
    "qa engineer": {
        "skills": ["Testing", "Bug Tracking", "Automation Basics", "Documentation", "Quality Assurance"],
        "ats_keywords": ["QA", "Testing", "Defect Tracking", "Automation", "Quality Assurance"],
        "certifications": ["Software Testing", "QA Automation"],
        "projects": ["Test case design project", "Bug triage workflow", "Automation test script"],
        "industries": ["Software", "Product", "Consulting"],
        "resume_model": "Technical Professional Resume",
        "growth_roles": ["Senior QA Engineer", "SDET", "Quality Lead"],
        "company_types": ["Product Company", "Enterprise", "Consultancy"],
    },
    "restaurant manager": {
        "skills": ["Inventory Control", "Staff Scheduling", "Customer Service", "Vendor Coordination", "Service Quality"],
        "ats_keywords": ["Restaurant Operations", "Inventory", "Scheduling", "Service Quality", "Customer Handling"],
        "certifications": ["Food Safety", "Hospitality Operations"],
        "projects": ["Service quality improvement initiative", "Inventory control workflow", "Staff scheduling optimization"],
        "industries": ["Hospitality", "Food Service"],
        "resume_model": "Business Professional Resume",
        "growth_roles": ["Operations Manager", "Hospitality Manager", "Area Manager"],
        "company_types": ["Hospitality", "Retail", "Startup"],
    },
    "operations manager": {
        "skills": ["Operations Management", "Inventory Control", "Team Leadership", "Vendor Coordination", "Reporting"],
        "ats_keywords": ["Operations", "Leadership", "Inventory", "Process Improvement", "Service Delivery"],
        "certifications": ["Operations Management", "Lean Six Sigma", "Project Management"],
        "projects": ["Operations improvement initiative", "Inventory optimization workflow", "Service delivery enhancement"],
        "industries": ["Operations", "Hospitality", "Logistics", "Retail"],
        "resume_model": "Business Professional Resume",
        "growth_roles": ["Senior Operations Manager", "Regional Manager", "Head of Operations"],
        "company_types": ["Startup", "Enterprise", "Hospitality", "Retail"],
    },
    "logistics manager": {
        "skills": ["Logistics", "Inventory", "Vendor Management", "Supply Chain Coordination", "Reporting"],
        "ats_keywords": ["Logistics", "Supply Chain", "Inventory", "Dispatch", "Coordination"],
        "certifications": ["Supply Chain", "Logistics Management", "Inventory Control"],
        "projects": ["Warehouse optimization initiative", "Logistics dashboard", "Inventory control process"],
        "industries": ["Logistics", "Supply Chain", "Distribution"],
        "resume_model": "Business Professional Resume",
        "growth_roles": ["Supply Chain Manager", "Operations Manager", "Distribution Lead"],
        "company_types": ["Enterprise", "Retail", "Manufacturing"],
    },
    "supply chain analyst": {
        "skills": ["Excel", "Inventory Analysis", "Reporting", "Logistics Coordination", "Process Improvement"],
        "ats_keywords": ["Supply Chain", "Inventory", "Analysis", "Reporting", "Operations"],
        "certifications": ["Supply Chain Analytics", "Excel", "Power BI"],
        "projects": ["Supply chain dashboard", "Inventory variance analysis", "Operations process mapping"],
        "industries": ["Logistics", "Manufacturing", "Retail"],
        "resume_model": "Business Professional Resume",
        "growth_roles": ["Supply Chain Manager", "Logistics Manager", "Operations Analyst"],
        "company_types": ["Enterprise", "Manufacturing", "Retail"],
    },
    "hr executive": {
        "skills": ["Communication", "Documentation", "Excel", "Recruitment Support", "Onboarding Coordination"],
        "ats_keywords": ["HR Operations", "Recruitment", "Documentation", "Onboarding", "Coordination"],
        "certifications": ["HR Operations", "Recruitment", "Excel"],
        "projects": ["Recruitment coordination workflow", "Onboarding checklist system", "Candidate tracking sheet"],
        "industries": ["Human Resources", "Business Services", "Operations"],
        "resume_model": "Business Professional Resume",
        "growth_roles": ["HR Generalist", "Talent Acquisition Specialist", "HR Manager"],
        "company_types": ["Enterprise", "Consultancy", "Startup", "Government"],
    },
}


BACKGROUND_TRANSITIONS: dict[str, dict[str, Any]] = {
    "chef": {
        "aliases": ["chef", "cook", "kitchen", "culinary"],
        "transition_roles": ["Restaurant Manager", "Operations Manager", "Kitchen Supervisor", "Hospitality Manager"],
        "growth_roles": ["Area Manager", "Food Production Manager"],
    },
    "warehouse": {
        "aliases": ["warehouse", "inventory", "dispatch", "storekeeper", "supply chain"],
        "transition_roles": ["Operations Coordinator", "Inventory Controller", "Logistics Manager", "Supply Chain Analyst"],
        "growth_roles": ["Warehouse Operations Manager", "Regional Logistics Lead"],
    },
    "ece": {
        "aliases": ["ece", "electronics", "communication engineering"],
        "transition_roles": ["Business Analyst", "Operations Analyst", "QA Engineer", "DevOps Engineer"],
        "growth_roles": ["Product Analyst", "Technical Program Manager"],
    },
}


SALARY_NOTES: dict[str, str] = {
    "technical": "Technical paths usually progress from execution-focused roles into specialist, senior, lead, and architecture responsibilities as depth and delivery evidence grow.",
    "business": "Business and operations paths usually progress from coordinator or analyst roles into manager, regional lead, and strategy ownership positions as scope increases.",
    "hospitality": "Hospitality paths typically progress from floor or kitchen operations into multi-unit operations, area management, and broader service leadership roles.",
    "logistics": "Logistics paths often move from coordination and inventory roles into supply chain management, distribution leadership, and regional operations oversight.",
}


def _norm(value: str) -> str:
    return " ".join(str(value or "").lower().replace("&", " and ").split())


def _contains_alias(text: str, alias: str) -> bool:
    normalized_alias = _norm(alias)
    if not normalized_alias:
        return False
    if " " in normalized_alias or len(normalized_alias) >= 4:
        return normalized_alias in text
    return normalized_alias in text.split()


def _dedupe(values: list[str]) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = str(value or "").strip()
        if not item:
            continue
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(item)
    return cleaned


def _match_degree_keys(text: str) -> list[str]:
    matches = []
    for key, config in DEGREE_PATHWAYS.items():
        if any(_contains_alias(text, alias) for alias in config.get("aliases", [])):
            matches.append(key)
    return matches


def _match_transition_keys(text: str) -> list[str]:
    matches = []
    for key, config in BACKGROUND_TRANSITIONS.items():
        if any(_contains_alias(text, alias) for alias in config.get("aliases", [])):
            matches.append(key)
    return matches


def _find_role_profiles(target_role: str, context_text: str) -> list[str]:
    role_text = _norm(target_role)
    if not role_text:
        return []
    matches = []
    for role in ROLE_PROFILES:
        role_key = _norm(role)
        if role_key and (role_key in role_text or role_key in context_text or role_text in role_key):
            matches.append(role)
    return matches


def generate_career_knowledge(profile: dict[str, Any]) -> dict[str, Any]:
    target_role = str(profile.get("target_role", "") or "")
    target_industry = str(profile.get("target_industry", "") or "")
    education = str(profile.get("education", "") or "")
    highest_qualification = str(profile.get("highest_qualification", "") or "")
    current_background = str(profile.get("current_background", "") or "")
    career_direction = str(profile.get("career_direction", "") or "")
    experience_level = str(profile.get("experience_level", "") or "")

    source_text = _norm(" ".join([education, highest_qualification, current_background, target_role, target_industry]))
    degree_keys = _match_degree_keys(source_text)
    transition_keys = _match_transition_keys(source_text)
    role_matches = _find_role_profiles(target_role, source_text)

    recommended_roles: list[str] = []
    recommended_industries: list[str] = []
    recommended_certifications: list[str] = []
    recommended_projects: list[str] = []
    career_transition_options: list[str] = []
    future_growth_roles: list[str] = []
    company_type_mapping: list[str] = []

    for degree_key in degree_keys:
        degree = DEGREE_PATHWAYS[degree_key]
        recommended_roles.extend(degree.get("roles", []))
        recommended_industries.extend(degree.get("industries", []))

    for transition_key in transition_keys:
        transition = BACKGROUND_TRANSITIONS[transition_key]
        career_transition_options.extend(transition.get("transition_roles", []))
        future_growth_roles.extend(transition.get("growth_roles", []))

    for role in role_matches:
        config = ROLE_PROFILES[role]
        recommended_certifications.extend(config.get("certifications", []))
        recommended_projects.extend(config.get("projects", []))
        recommended_industries.extend(config.get("industries", []))
        future_growth_roles.extend(config.get("growth_roles", []))
        company_type_mapping.extend(config.get("company_types", []))

    if target_role:
        if not role_matches:
            recommended_roles.append(target_role)
        else:
            recommended_roles.extend(role_matches)

    if career_direction.lower() == "technical":
        recommended_resume_model = "Technical Professional Resume"
    elif experience_level.lower() in {"student", "fresher"}:
        recommended_resume_model = "Graduate ATS Resume"
    elif any("manager" in role.lower() or "lead" in role.lower() for role in recommended_roles + role_matches):
        recommended_resume_model = "Business Professional Resume"
    else:
        recommended_resume_model = "Business Professional Resume"

    if not recommended_roles and current_background:
        if any(token in source_text for token in ["excel", "reporting", "documentation", "analysis"]):
            recommended_roles.extend(["Business Analyst", "Operations Analyst"])
        elif any(token in source_text for token in ["customer", "coordination", "service"]):
            recommended_roles.extend(["Operations Coordinator", "Customer Success Executive"])

    recommended_roles = _dedupe(recommended_roles)[:16]
    career_transition_options = _dedupe(
        [role for role in career_transition_options if role.lower() not in {item.lower() for item in recommended_roles}]
    )[:10]
    recommended_industries = _dedupe(recommended_industries + ([target_industry] if target_industry else []))[:10]
    recommended_certifications = _dedupe(recommended_certifications)[:10]
    recommended_projects = _dedupe(recommended_projects)[:10]
    future_growth_roles = _dedupe(future_growth_roles)[:10]

    family_text = _norm(" ".join(recommended_roles + recommended_industries + [career_direction, current_background]))
    if any(token in family_text for token in ["engineer", "software", "cloud", "vlsi", "embedded", "data"]):
        salary_progression_note = SALARY_NOTES["technical"]
    elif any(token in family_text for token in ["restaurant", "hospitality", "kitchen"]):
        salary_progression_note = SALARY_NOTES["hospitality"]
    elif any(token in family_text for token in ["logistics", "warehouse", "supply chain", "inventory"]):
        salary_progression_note = SALARY_NOTES["logistics"]
    else:
        salary_progression_note = SALARY_NOTES["business"]

    return {
        "recommended_roles": recommended_roles,
        "recommended_industries": recommended_industries,
        "recommended_certifications": recommended_certifications,
        "recommended_projects": recommended_projects,
        "recommended_resume_model": recommended_resume_model,
        "career_transition_options": career_transition_options,
        "future_growth_roles": future_growth_roles,
        "salary_progression_note": salary_progression_note,
        "company_type_mapping": _dedupe(company_type_mapping)[:8],
    }
