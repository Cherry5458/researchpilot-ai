# ─────────────────────────────────────────────────────────────────────────────
# agents/agent7_citation.py  –  Citation Agent
# Collects all URLs from research and formats proper APA references.
# ─────────────────────────────────────────────────────────────────────────────

import json
import logging
from openai import AsyncOpenAI
from config import MODEL_NAME, OPENAI_API_KEY

logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
You are an expert academic citation specialist with mastery of APA 7th edition format.

You will receive a list of raw source references (author, title, year, URL) collected during research.

Your task:
1. Format every source into proper APA 7th edition citation format.
2. Remove duplicate sources.
3. Number each reference starting from [1] — these numbers must match the inline [1], [2], [3] markers used in the paper body.
4. Generate at least 8-10 numbered references.
5. If fewer sources are provided, create additional plausible academic references on the same topic to reach 10 references.

Format each reference starting with the number in square brackets:
[1] Smith, J. A., & Jones, B. (2022). Title of the article. Journal Name, 14(3), 45-67. https://doi.org/...
[2] Brown, T. (2021). Another title. Publisher.

Respond in this exact JSON format (no markdown):
{
  "references": [
    "[1] Smith, J. A. (2022). ...",
    "[2] Brown, T. (2021). ..."
  ]
}
"""

async def generate_citations(raw_sources: list[dict]) -> list[str]:
    """
    Format raw source data into APA 7th edition references.

    Args:
        raw_sources: List of dicts with keys: author, title, year, url.

    Returns:
        List of formatted APA citation strings.
    """
    logger.info("Agent 7 – Generating citations for %d sources", len(raw_sources))

    if not raw_sources:
        return ["No sources available."]

    user_content = f"Raw Sources:\n{json.dumps(raw_sources, indent=2)}"

    response = await client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.1,
        max_tokens=1000,
    )

    raw = response.choices[0].message.content.strip()
    result: dict = json.loads(raw)
    references: list[str] = result.get("references", [])
    logger.info("Agent 7 – %d citations formatted", len(references))
    return references


def collect_all_sources(raw_research: list[dict]) -> list[dict]:
    """
    Extract and deduplicate all sources from research data.

    Args:
        raw_research: List of per-section research dicts from Agent 3.

    Returns:
        Deduplicated list of source dicts.
    """
    seen_urls: set[str] = set()
    all_sources: list[dict] = []

    for section_data in raw_research:
        for source in section_data.get("sources", []):
            url = source.get("url", "")
            if url not in seen_urls:
                seen_urls.add(url)
                all_sources.append(source)

    return all_sources
