# ─────────────────────────────────────────────────────────────────────────────
# agents/agent3_researcher.py  –  Research Agent
# Searches for facts, statistics, concepts and recent findings per section.
# ─────────────────────────────────────────────────────────────────────────────

import json
import logging
from openai import AsyncOpenAI
from config import MODEL_NAME, OPENAI_API_KEY

logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
You are an expert academic researcher with deep knowledge across all domains.
Given a research topic, keywords, and a specific section plan, gather comprehensive information.

You must produce:
- facts: concrete factual statements relevant to this section
- statistics: numerical data, percentages, study results (with approximate years)
- recent_findings: developments from the last 3-5 years
- key_concepts: domain-specific terms and brief definitions
- sources: 2-3 plausible academic/reputable source references (author, title, year, URL format)

Ensure no duplicate information. Be specific and detailed.

Respond in this exact JSON format (no markdown):
{
  "section": "<section title>",
  "facts": ["fact1", "fact2", "fact3", "fact4", "fact5"],
  "statistics": ["stat1", "stat2", "stat3"],
  "recent_findings": ["finding1", "finding2", "finding3"],
  "key_concepts": [{"term": "...", "definition": "..."}],
  "sources": [
    {"author": "...", "title": "...", "year": "...", "url": "https://..."}
  ]
}
"""

async def research_section(
    topic: str,
    keywords: list[str],
    section_title: str,
    section_objective: str,
    key_points: list[str],
) -> dict:
    """
    Research one section of the paper.

    Args:
        topic: Validated research topic.
        keywords: Research keywords.
        section_title: Name of the section to research.
        section_objective: What this section must accomplish.
        key_points: Bullet points to cover.

    Returns:
        dict with facts, statistics, recent_findings, key_concepts, sources.
    """
    logger.info("Agent 3 – Researching section: %s", section_title)

    user_content = (
        f"Topic: {topic}\n"
        f"Keywords: {', '.join(keywords)}\n"
        f"Section: {section_title}\n"
        f"Objective: {section_objective}\n"
        f"Key Points to Cover:\n" + "\n".join(f"- {p}" for p in key_points)
    )

    response = await client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.5,
        max_tokens=1000,
    )

    raw = response.choices[0].message.content.strip()
    result: dict = json.loads(raw)
    logger.info("Agent 3 – Section '%s' research complete", section_title)
    return result


async def research_all_sections(
    topic: str, keywords: list[str], sections: list[dict]
) -> list[dict]:
    """
    Research every section sequentially and return compiled results.

    Args:
        topic: Validated topic.
        keywords: Research keywords.
        sections: List of section plan dicts from Agent 2.

    Returns:
        List of research result dicts, one per section.
    """
    results: list[dict] = []
    for section in sections:
        # Skip References — citations are handled by Agent 7
        if section["section_title"].lower() == "references":
            continue
        data = await research_section(
            topic=topic,
            keywords=keywords,
            section_title=section["section_title"],
            section_objective=section["objective"],
            key_points=section["key_points"],
        )
        results.append(data)
    return results
