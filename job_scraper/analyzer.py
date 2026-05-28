"""
analyzer.py — Uses Claude API to intelligently score and enrich job listings.

For each batch of jobs, Claude:
  1. Scores relevance (0–10) against your profile
  2. Identifies why you match (or don't)
  3. Flags German-language requirements
  4. Extracts key skills required
  5. Suggests tailoring tips for your cover letter
"""

import os
import json
import logging
from anthropic import Anthropic
from config import CANDIDATE, SKILLS, JOB_PREFERENCES, CLAUDE

logger = logging.getLogger(__name__)
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))


SYSTEM_PROMPT = """You are a professional career advisor helping a job seeker in Germany.
You analyze job listings and score them against a candidate's profile.
Always respond with valid JSON only — no markdown, no explanation outside the JSON."""


def build_analysis_prompt(jobs: list[dict], category: str) -> str:
    candidate_summary = f"""
CANDIDATE PROFILE:
- Name: {CANDIDATE['name']}
- Location: {CANDIDATE['location']}
- Study: {CANDIDATE['current_study']}
- Languages: English C1, German A2, Persian native
- Work permit: Werkstudent (max 20 hrs/week during semester)
- Skills: {', '.join(SKILLS[:25])}

PREFERENCES:
- Part-time only
- Prefer English-friendly workplaces
- Avoid roles requiring German B2+
- Max commute: 60km from Aachen
"""

    jobs_json = json.dumps(
        [{"id": i, "title": j["title"], "company": j["company"],
          "location": j["location"], "description": j["description"],
          "employment_type": j.get("employment_type", ""),
          "source": j.get("source", "")}
         for i, j in enumerate(jobs)],
        ensure_ascii=False, indent=2
    )

    return f"""
{candidate_summary}

JOBS TO ANALYZE (category: {category}):
{jobs_json}

For each job, return a JSON array where each item has:
{{
  "id": <same id as input>,
  "relevance_score": <0-10, 10=perfect match>,
  "match_reasons": ["reason 1", "reason 2"],
  "concerns": ["concern 1"] or [],
  "german_required": true/false,
  "key_skills_required": ["skill1", "skill2"],
  "cover_letter_tip": "One specific tip to tailor application",
  "recommendation": "APPLY" | "CONSIDER" | "SKIP"
}}

Rules:
- Score 8-10: Strong match, APPLY
- Score 5-7: Partial match, CONSIDER
- Score 0-4: Poor match or German B2+ required, SKIP
- If German B2+ is explicitly required and candidate is A2, recommendation must be SKIP
- Return ONLY valid JSON array, nothing else.
"""


def analyze_jobs(jobs: list[dict], category: str) -> list[dict]:
    """
    Send jobs to Claude for analysis. Returns enriched job dicts.
    Processes in batches of 8 to stay within token limits.
    """
    if not jobs:
        return []

    enriched = []
    batch_size = 8

    for i in range(0, len(jobs), batch_size):
        batch = jobs[i:i + batch_size]
        logger.info(f"  Analyzing batch {i//batch_size + 1} ({len(batch)} jobs, {category})...")

        try:
            response = client.messages.create(
                model=CLAUDE["model"],
                max_tokens=CLAUDE["max_tokens"],
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": build_analysis_prompt(batch, category)}]
            )

            raw = response.content[0].text.strip()
            # Strip accidental markdown fences
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            analyses = json.loads(raw)

            # Merge analysis back into job dicts
            analysis_map = {a["id"]: a for a in analyses}
            for j, job in enumerate(batch):
                analysis = analysis_map.get(j, {})
                enriched.append({**job, **analysis})

        except json.JSONDecodeError as e:
            logger.error(f"  Claude JSON parse error: {e}")
            # Return jobs without analysis rather than failing
            enriched.extend(batch)
        except Exception as e:
            logger.error(f"  Claude API error: {e}")
            enriched.extend(batch)

    # Sort by relevance score descending
    enriched.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    return enriched


def filter_and_rank(jobs: list[dict], max_results: int = 15) -> list[dict]:
    """Filter out SKIPs and return top N jobs."""
    filtered = [j for j in jobs if j.get("recommendation", "CONSIDER") != "SKIP"]
    return filtered[:max_results]
