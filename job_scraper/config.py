# ============================================================
#  config.py — Your personal job search profile
#  Edit this file to update your skills, preferences, or
#  search keywords. The daily report will adapt automatically.
# ============================================================

# ── Candidate Profile ────────────────────────────────────────
CANDIDATE = {
    "name": "Arash Karimi",
    "location": "Aachen, Germany",
    "region": "Nordrhein-Westfalen (NRW)",
    "current_study": "MSc Human-Centered Intelligent Systems, RWTH Aachen",
    "languages": {"English": "C1", "German": "A2", "Persian": "Native"},
    "work_permit": "EU student — eligible for Werkstudent (20 hrs/week during semester)",
}

# ── Technical Skills ─────────────────────────────────────────
SKILLS = [
    # Networking & Infrastructure
    "Network Engineering", "Cisco Routing & Switching", "FortiGate Firewall",
    "VMware ESXi", "Active Directory", "Microsoft Exchange Server",
    "KerioControl VPN", "IT Supervision", "Linux Administration",

    # Software & Development
    "Python", "T-SQL", "Docker", "Microservices", "REST APIs",
    "MATLAB", "C", "Git", "GitHub",

    # AI / ML
    "Machine Learning", "Deep Learning", "Graph Neural Networks (GNN)",
    "Convolutional Neural Networks (CNN)", "TensorFlow", "PyTorch",
    "Natural Language Processing", "Computer Vision",

    # AI Tools (modern)
    "Claude (Anthropic) — AI-assisted workflows & automation",
    "Prompt Engineering", "LLM Integration",

    # Cloud & DevOps
    "Cloud Computing", "Microservice Scheduling", "Docker Compose",

    # Databases
    "SQL Server", "Database Administration", "T-SQL",

    # Soft Skills
    "Technical Documentation", "Research & Publication",
    "Team Leadership", "IT Project Management",
]

# ── Job Search Preferences ───────────────────────────────────
JOB_PREFERENCES = {
    "type": "part-time",                  # part-time / Werkstudent / mini-job
    "max_hours_per_week": 20,
    "prefer_english": True,               # prioritize English-friendly roles
    "min_german_level": "A2",            # skip jobs requiring B2+ German
    "remote_ok": True,
    "hybrid_ok": True,
    "onsite_ok": True,
    "commute_radius_km": 60,             # from Aachen (covers Cologne, Düsseldorf)
}

# ── Category 1: Professional Search Queries ─────────────────
# These target roles matching your CV
PROFESSIONAL_QUERIES = [
    "working student machine learning Aachen",
    "Werkstudent IT network engineer NRW English",
    "part time AI developer student Aachen",
    "working student cybersecurity NRW English",
    "Werkstudent cloud computing Python Aachen",
    "student IT infrastructure Aachen RWTH",
    "part time deep learning research assistant NRW",
    "working student data science Aachen English",
    "Werkstudent software developer Python Aachen",
    "HiWi AI research RWTH Aachen",
]

# ── Category 2: General Part-Time Queries ───────────────────
# Warehouse, logistics, packaging — no German required
GENERAL_QUERIES = [
    "part time warehouse worker Aachen no German",
    "Lagerhelfer Aachen Teilzeit",
    "food packaging part time NRW English",
    "order picker Aachen part time",
    "Amazon fulfillment NRW part time",
    "mini job Aachen student English",
    "production assistant part time Eschweiler",
    "student aushilfe Aachen English",
]

# ── Platforms ────────────────────────────────────────────────
PLATFORMS = {
    "stepstone": {
        "enabled": True,
        "base_url": "https://www.stepstone.de",
        "search_path": "/jobs/{query}/in-{location}",
    },
    "indeed": {
        "enabled": True,
        "base_url": "https://de.indeed.com",
        "search_path": "/jobs?q={query}&l={location}",
    },
    "linkedin": {
        "enabled": True,
        "base_url": "https://www.linkedin.com",
        "search_path": "/jobs/search/?keywords={query}&location={location}",
    },
}

# ── Output Settings ──────────────────────────────────────────
OUTPUT = {
    "reports_dir": "output/reports",
    "docs_dir": "docs",                  # GitHub Pages serves from here
    "generate_docx": True,
    "generate_html": True,
    "generate_json": True,               # raw data for future use
    "max_jobs_per_category": 15,
    "date_format": "%Y-%m-%d",
}

# ── Claude API Settings ──────────────────────────────────────
CLAUDE = {
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 4000,
    "temperature": 0.2,                  # low = consistent, structured output
}
