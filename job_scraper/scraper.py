"""
scraper.py — Fetches job listings from Stepstone, Indeed, and LinkedIn.

Uses SerpAPI (free tier: 100 searches/month) to get structured results
without triggering bot-detection on job sites.

Free SerpAPI key: https://serpapi.com/  (100 free searches/month)
"""

import os
import time
import json
import logging
import requests
from datetime import datetime
from typing import Optional
from config import PROFESSIONAL_QUERIES, GENERAL_QUERIES, PLATFORMS, JOB_PREFERENCES, CANDIDATE

logger = logging.getLogger(__name__)

SERPAPI_KEY = os.environ.get("SERPAPI_KEY", "")
SERPAPI_URL = "https://serpapi.com/search"


# ─────────────────────────────────────────────
#  Core fetcher
# ─────────────────────────────────────────────

def fetch_jobs_serpapi(query: str, location: str = "Aachen, Germany", num: int = 10) -> list[dict]:
    """
    Fetch job listings using SerpAPI Google Jobs endpoint.
    Falls back to mock data if no API key is configured (for testing).
    """
    if not SERPAPI_KEY:
        logger.warning("No SERPAPI_KEY found — using mock data for testing.")
        return _mock_jobs(query, location)

    params = {
        "engine": "google_jobs",
        "q": query,
        "location": location,
        "hl": "en",
        "gl": "de",
        "api_key": SERPAPI_KEY,
        "num": num,
    }

    try:
        resp = requests.get(SERPAPI_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        jobs = data.get("jobs_results", [])
        logger.info(f"  SerpAPI → '{query}': {len(jobs)} results")
        return [_normalize(j) for j in jobs]
    except requests.RequestException as e:
        logger.error(f"  SerpAPI error for '{query}': {e}")
        return []


def _normalize(raw: dict) -> dict:
    """Convert SerpAPI job result to our standard format."""
    return {
        "title": raw.get("title", ""),
        "company": raw.get("company_name", ""),
        "location": raw.get("location", ""),
        "description": raw.get("description", "")[:800],  # truncate for Claude
        "posted": raw.get("detected_extensions", {}).get("posted_at", ""),
        "employment_type": raw.get("detected_extensions", {}).get("schedule_type", ""),
        "apply_url": _extract_url(raw),
        "source": _detect_source(raw),
        "thumbnail": raw.get("thumbnail", ""),
        "scraped_at": datetime.utcnow().isoformat(),
    }


def _extract_url(raw: dict) -> str:
    """Extract the best apply URL from a SerpAPI job result."""
    # Try apply options first
    apply_options = raw.get("apply_options", [])
    if apply_options:
        # Prefer Stepstone, Indeed, LinkedIn
        for preferred in ["stepstone", "indeed", "linkedin"]:
            for opt in apply_options:
                if preferred in opt.get("link", "").lower():
                    return opt["link"]
        return apply_options[0].get("link", "")

    # Fallback: job_id Google link
    job_id = raw.get("job_id", "")
    if job_id:
        return f"https://www.google.com/search?q={job_id}"

    return ""


def _detect_source(raw: dict) -> str:
    """Detect which platform the job came from."""
    url = _extract_url(raw).lower()
    if "stepstone" in url:
        return "Stepstone"
    if "indeed" in url:
        return "Indeed"
    if "linkedin" in url:
        return "LinkedIn"
    return "Google Jobs"


# ─────────────────────────────────────────────
#  Main scrape function
# ─────────────────────────────────────────────

def scrape_all_jobs() -> dict:
    """
    Run all search queries and return categorized job listings.
    Returns: {"professional": [...], "general": [...]}
    """
    location = f"{CANDIDATE['location']}, {CANDIDATE['region']}"
    results = {"professional": [], "general": []}

    logger.info("=== Scraping PROFESSIONAL jobs ===")
    seen_titles = set()
    for query in PROFESSIONAL_QUERIES:
        jobs = fetch_jobs_serpapi(query, location=location, num=5)
        for job in jobs:
            key = f"{job['title'].lower()}|{job['company'].lower()}"
            if key not in seen_titles and job["title"]:
                seen_titles.add(key)
                job["category"] = "professional"
                results["professional"].append(job)
        time.sleep(1.2)   # be polite to the API

    logger.info("=== Scraping GENERAL jobs ===")
    seen_titles_g = set()
    for query in GENERAL_QUERIES:
        jobs = fetch_jobs_serpapi(query, location=location, num=5)
        for job in jobs:
            key = f"{job['title'].lower()}|{job['company'].lower()}"
            if key not in seen_titles_g and job["title"]:
                seen_titles_g.add(key)
                job["category"] = "general"
                results["general"].append(job)
        time.sleep(1.2)

    logger.info(
        f"Scraping done: {len(results['professional'])} professional, "
        f"{len(results['general'])} general jobs found."
    )
    return results


# ─────────────────────────────────────────────
#  Mock data (used when no API key is set)
# ─────────────────────────────────────────────

def _mock_jobs(query: str, location: str) -> list[dict]:
    """Return mock job data for testing without an API key."""
    return [
        {
            "title": f"[MOCK] Working Student – {query.title()}",
            "company": "Example GmbH",
            "location": location,
            "description": (
                f"This is a mock job listing for query '{query}'. "
                "In production, real listings will appear here from Stepstone, Indeed, and LinkedIn. "
                "Skills required: Python, machine learning, English fluency."
            ),
            "posted": "1 day ago",
            "employment_type": "Part-time",
            "apply_url": "https://de.indeed.com/jobs?q=working+student+it+aachen",
            "source": "Mock Data",
            "thumbnail": "",
            "scraped_at": datetime.utcnow().isoformat(),
            "category": "professional",
        }
    ]
