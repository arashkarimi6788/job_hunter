"""
main.py — Daily Job Hunter entry point.

Pipeline:
  1. Scrape job listings (Stepstone, Indeed, LinkedIn via SerpAPI)
  2. Analyze & score each job with Claude API
  3. Generate Word (.docx) + HTML report
  4. Save JSON data file
  5. GitHub Actions commits everything back to the repo
"""

import os
import sys
import logging
from pathlib import Path

# Make sure imports work whether run from project root or job_scraper/
sys.path.insert(0, str(Path(__file__).parent))

from config import OUTPUT
from scraper import scrape_all_jobs
from analyzer import analyze_jobs, filter_and_rank
from report_generator import generate_docx, generate_html, save_json

# ── Logging setup ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("job_hunter.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 60)
    logger.info("  Job Hunter Bot — starting daily run")
    logger.info("=" * 60)

    # ── Ensure output dirs exist ───────────────────────────────
    reports_dir = OUTPUT["reports_dir"]
    docs_dir = OUTPUT["docs_dir"]
    Path(reports_dir).mkdir(parents=True, exist_ok=True)
    Path(docs_dir).mkdir(parents=True, exist_ok=True)

    # ── Step 1: Scrape ─────────────────────────────────────────
    logger.info("[1/4] Scraping job listings...")
    raw = scrape_all_jobs()
    logger.info(
        f"      Raw results: {len(raw['professional'])} professional, "
        f"{len(raw['general'])} general"
    )

    # ── Step 2: Analyze with Claude ───────────────────────────
    logger.info("[2/4] Analyzing jobs with Claude...")
    pro_analyzed = analyze_jobs(raw["professional"], category="professional")
    gen_analyzed = analyze_jobs(raw["general"], category="general")

    # Filter out poor matches and cap to max_results
    max_r = OUTPUT["max_jobs_per_category"]
    pro_final = filter_and_rank(pro_analyzed, max_results=max_r)
    gen_final = filter_and_rank(gen_analyzed, max_results=max_r)

    logger.info(
        f"      After filtering: {len(pro_final)} professional, "
        f"{len(gen_final)} general"
    )

    # ── Step 3: Generate reports ───────────────────────────────
    logger.info("[3/4] Generating reports...")

    if OUTPUT["generate_docx"]:
        docx_path = generate_docx(pro_final, gen_final, reports_dir)
        logger.info(f"      Word report: {docx_path}")

    if OUTPUT["generate_html"]:
        html_path = generate_html(pro_final, gen_final, reports_dir, docs_dir)
        logger.info(f"      HTML report: {html_path}")

    if OUTPUT["generate_json"]:
        json_path = save_json(pro_final, gen_final, reports_dir)
        logger.info(f"      JSON data:   {json_path}")

    # ── Step 4: Summary ────────────────────────────────────────
    logger.info("[4/4] Done!")
    apply_count = sum(
        1 for j in pro_final + gen_final
        if j.get("recommendation") == "APPLY"
    )
    logger.info(f"      Total jobs in report: {len(pro_final) + len(gen_final)}")
    logger.info(f"      Jobs to APPLY NOW:    {apply_count}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
