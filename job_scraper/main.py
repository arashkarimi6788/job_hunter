"""
main.py — Daily Job Hunter entry point.
"""

import os
import sys
import logging
from pathlib import Path

# Always resolve paths relative to the repo root (one level up from job_scraper/)
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent))

from config import OUTPUT
from scraper import scrape_all_jobs
from analyzer import analyze_jobs, filter_and_rank
from report_generator import generate_docx, generate_html, save_json

# ── Logging ───────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 60)
    logger.info("  Job Hunter Bot — starting daily run")
    logger.info("=" * 60)

    # ── Ensure output dirs exist (always relative to repo root) ──
    reports_dir = str(REPO_ROOT / OUTPUT["reports_dir"])
    docs_dir    = str(REPO_ROOT / OUTPUT["docs_dir"])
    Path(reports_dir).mkdir(parents=True, exist_ok=True)
    Path(docs_dir).mkdir(parents=True, exist_ok=True)
    logger.info(f"Output dir: {reports_dir}")
    logger.info(f"Docs dir:   {docs_dir}")

    # ── Step 1: Scrape ────────────────────────────────────────
    logger.info("[1/4] Scraping job listings...")
    raw = scrape_all_jobs()
    logger.info(f"      Raw: {len(raw['professional'])} professional, {len(raw['general'])} general")

    # ── Step 2: Analyze with Claude ──────────────────────────
    logger.info("[2/4] Analyzing with Claude...")
    pro_analyzed = analyze_jobs(raw["professional"], category="professional")
    gen_analyzed = analyze_jobs(raw["general"],      category="general")

    max_r     = OUTPUT["max_jobs_per_category"]
    pro_final = filter_and_rank(pro_analyzed, max_results=max_r)
    gen_final = filter_and_rank(gen_analyzed, max_results=max_r)
    logger.info(f"      After filter: {len(pro_final)} professional, {len(gen_final)} general")

    # ── Step 3: Generate reports ──────────────────────────────
    logger.info("[3/4] Generating reports...")
    if OUTPUT["generate_docx"]:
        generate_docx(pro_final, gen_final, reports_dir)
    if OUTPUT["generate_html"]:
        generate_html(pro_final, gen_final, reports_dir, docs_dir)
    if OUTPUT["generate_json"]:
        save_json(pro_final, gen_final, reports_dir)

    # ── Step 4: Summary ───────────────────────────────────────
    apply_count = sum(1 for j in pro_final + gen_final if j.get("recommendation") == "APPLY")
    logger.info("[4/4] Done!")
    logger.info(f"      Total in report : {len(pro_final) + len(gen_final)}")
    logger.info(f"      Apply now       : {apply_count}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
