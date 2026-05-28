"""
scraper.py — Fetches job listings via two strategies:

  Strategy A (primary): SerpAPI Google Jobs — structured, reliable
  Strategy B (fallback): Direct Indeed RSS + Arbeitsagentur API — no key needed

If SERPAPI_KEY is set → uses Strategy A for best results.
If not set           → uses Strategy B (free, no limits, no key required).
"""

import os
import time
import json
import logging
import requests
import urllib.parse
from datetime import datetime
from xml.etree import ElementTree as ET

from config import PROFESSIONAL_QUERIES, GENERAL_QUERIES, CANDIDATE

logger = logging.getLogger(__name__)

SERPAPI_KEY  = os.environ.get("SERPAPI_KEY", "").strip()
SERPAPI_URL  = "https://serpapi.com/search"
HEADERS      = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


# ─────────────────────────────────────────────────────────────
#  Strategy A — SerpAPI  (best quality, needs free API key)
# ─────────────────────────────────────────────────────────────

def fetch_via_serpapi(query: str, location: str, num: int = 8) -> list[dict]:
    params = {
        "engine":   "google_jobs",
        "q":        query,
        "location": location,
        "hl":       "en",
        "gl":       "de",
        "api_key":  SERPAPI_KEY,
        "num":      num,
    }
    try:
        r = requests.get(SERPAPI_URL, params=params, timeout=15)
        r.raise_for_status()
        jobs = r.json().get("jobs_results", [])
        logger.info(f"  SerpAPI '{query}': {len(jobs)} results")
        return [_norm_serpapi(j) for j in jobs]
    except Exception as e:
        logger.warning(f"  SerpAPI failed for '{query}': {e}")
        return []


def _norm_serpapi(raw: dict) -> dict:
    url = ""
    for opt in raw.get("apply_options", []):
        link = opt.get("link", "")
        if any(p in link.lower() for p in ["stepstone", "indeed", "linkedin"]):
            url = link
            break
    if not url and raw.get("apply_options"):
        url = raw["apply_options"][0].get("link", "")

    src = "Google Jobs"
    for p in ["stepstone", "indeed", "linkedin"]:
        if p in url.lower():
            src = p.capitalize()
            break

    return {
        "title":           raw.get("title", ""),
        "company":         raw.get("company_name", ""),
        "location":        raw.get("location", ""),
        "description":     raw.get("description", "")[:800],
        "posted":          raw.get("detected_extensions", {}).get("posted_at", ""),
        "employment_type": raw.get("detected_extensions", {}).get("schedule_type", "Part-time"),
        "apply_url":       url,
        "source":          src,
        "scraped_at":      datetime.utcnow().isoformat(),
    }


# ─────────────────────────────────────────────────────────────
#  Strategy B — Bundesagentur für Arbeit (BA) REST API
#  Free, official German job portal, no key needed.
#  Docs: https://jobsuche.api.bund.dev/
# ─────────────────────────────────────────────────────────────

BA_URL = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobs"
BA_AUTH = "jobboerse-jobsuche"          # public OAuth token for the open API

def fetch_via_arbeitsagentur(query: str, location: str = "Aachen", num: int = 8) -> list[dict]:
    """
    Query the official Bundesagentur für Arbeit job search API.
    This is a real, public REST API — no key required.
    """
    params = {
        "was":      query,          # job title / keywords
        "wo":       location,       # location
        "umkreis":  50,             # radius in km
        "arbeitszeit": "TEILZEIT",  # part-time filter
        "size":     num,
        "page":     1,
    }
    headers = {
        "X-API-Key": BA_AUTH,
        "Accept":    "application/json",
        "User-Agent": "Mozilla/5.0",
    }
    try:
        r = requests.get(BA_URL, params=params, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
        jobs_raw = data.get("stellenangebote") or []
        logger.info(f"  Arbeitsagentur '{query}': {len(jobs_raw)} results")
        return [_norm_ba(j) for j in jobs_raw]
    except Exception as e:
        logger.warning(f"  Arbeitsagentur failed for '{query}': {e}")
        return []


def _norm_ba(raw: dict) -> dict:
    ref = raw.get("refnr", "")
    url = f"https://www.arbeitsagentur.de/jobsuche/jobdetail/{ref}" if ref else \
          "https://www.arbeitsagentur.de/jobsuche/"

    employer = raw.get("arbeitgeber", "")
    title    = raw.get("titel", "")
    ort      = raw.get("arbeitsort", {})
    loc      = f"{ort.get('ort','')}, {ort.get('region','Germany')}".strip(", ")
    desc     = raw.get("stellenbeschreibung") or \
               f"{title} position at {employer} in {loc}. Part-time role listed on Bundesagentur für Arbeit."

    return {
        "title":           title,
        "company":         employer,
        "location":        loc,
        "description":     str(desc)[:800],
        "posted":          raw.get("eintrittsdatum", ""),
        "employment_type": "Part-time (Teilzeit)",
        "apply_url":       url,
        "source":          "Bundesagentur für Arbeit",
        "scraped_at":      datetime.utcnow().isoformat(),
    }


# ─────────────────────────────────────────────────────────────
#  Strategy C — Indeed RSS (secondary free fallback)
# ─────────────────────────────────────────────────────────────

def fetch_via_indeed_rss(query: str, location: str = "Aachen", num: int = 6) -> list[dict]:
    """
    Indeed exposes an RSS feed — no API key needed.
    """
    q   = urllib.parse.quote_plus(query)
    loc = urllib.parse.quote_plus(location)
    url = f"https://de.indeed.com/rss?q={q}&l={loc}&radius=50&sort=date&limit={num}&lang=en"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        items = root.findall(".//item")
        logger.info(f"  Indeed RSS '{query}': {len(items)} results")
        return [_norm_indeed_rss(i) for i in items]
    except Exception as e:
        logger.warning(f"  Indeed RSS failed for '{query}': {e}")
        return []


def _norm_indeed_rss(item) -> dict:
    def _t(tag):
        el = item.find(tag)
        return el.text.strip() if el is not None and el.text else ""

    desc_raw = _t("description")
    # strip basic HTML tags from RSS description
    import re
    desc = re.sub(r"<[^>]+>", " ", desc_raw).strip()[:800]

    return {
        "title":           _t("title"),
        "company":         _t("{com.indeed}employer"),
        "location":        _t("{com.indeed}city") or "Aachen, NRW",
        "description":     desc,
        "posted":          _t("pubDate"),
        "employment_type": "Part-time",
        "apply_url":       _t("link"),
        "source":          "Indeed",
        "scraped_at":      datetime.utcnow().isoformat(),
    }


# ─────────────────────────────────────────────────────────────
#  Main scrape orchestrator
# ─────────────────────────────────────────────────────────────

def scrape_all_jobs() -> dict:
    """
    Run all queries and return {"professional": [...], "general": [...]}.
    Automatically picks the best available strategy.
    """
    location = "Aachen, Germany"        # keep short for SerpAPI compatibility
    use_serpapi = bool(SERPAPI_KEY)

    if use_serpapi:
        logger.info("Strategy: SerpAPI (API key found)")
    else:
        logger.info("Strategy: Bundesagentur für Arbeit + Indeed RSS (no SerpAPI key — free mode)")

    results = {"professional": [], "general": []}

    # ── Professional queries ──────────────────────────────────
    logger.info("=== Scraping PROFESSIONAL jobs ===")
    seen = set()
    for query in PROFESSIONAL_QUERIES:
        if use_serpapi:
            jobs = fetch_via_serpapi(query, location=location, num=6)
        else:
            jobs  = fetch_via_arbeitsagentur(query, location="Aachen", num=6)
            jobs += fetch_via_indeed_rss(query, location="Aachen", num=4)

        for job in jobs:
            key = f"{job['title'].lower()}|{job['company'].lower()}"
            if key not in seen and job["title"]:
                seen.add(key)
                job["category"] = "professional"
                results["professional"].append(job)
        time.sleep(1.0)

    # ── General queries ───────────────────────────────────────
    logger.info("=== Scraping GENERAL jobs ===")
    seen_g = set()
    for query in GENERAL_QUERIES:
        if use_serpapi:
            jobs = fetch_via_serpapi(query, location=location, num=6)
        else:
            jobs  = fetch_via_arbeitsagentur(query, location="Aachen", num=6)
            jobs += fetch_via_indeed_rss(query, location="Aachen", num=4)

        for job in jobs:
            key = f"{job['title'].lower()}|{job['company'].lower()}"
            if key not in seen_g and job["title"]:
                seen_g.add(key)
                job["category"] = "general"
                results["general"].append(job)
        time.sleep(1.0)

    logger.info(
        f"Total scraped: {len(results['professional'])} professional, "
        f"{len(results['general'])} general"
    )
    return results
