# ─────────────────────────────────────────────────────────────────────────────
# services/topic_suggestions.py  –  Trending Topic Suggestions
# Returns 6 trending research topics across different domains.
# ─────────────────────────────────────────────────────────────────────────────

import logging
from openai import AsyncOpenAI
from config import MODEL_NAME, OPENAI_API_KEY
from utils.json_parser import safe_parse

logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
You are a research trend analyst with knowledge of the latest developments in technology,
medicine, environment, social sciences, and engineering.

Generate exactly 6 trending, highly researchable academic topics for 2025-2026.

Each topic must be:
- Specific and focused (not too broad)
- Current and relevant to recent developments
- Suitable for a 2500+ word academic research paper
- From different domains (AI, healthcare, environment, cybersecurity, etc.)

Respond ONLY in this exact JSON format (no markdown):
{
  "topics": [
    {
      "title": "Topic title here",
      "domain": "Artificial Intelligence",
      "why_trending": "One sentence reason why this is trending now."
    }
  ]
}
"""


async def get_trending_topics() -> list[dict]:
    """
    Get 6 trending research topic suggestions.

    Returns:
        List of dicts with title, domain, why_trending.
    """
    logger.info("Fetching trending topic suggestions")

    response = await client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": "Give me 6 trending research topics for 2025-2026."},
        ],
        temperature=0.8,
        max_tokens=800,
    )

    raw = response.choices[0].message.content.strip()
    result = safe_parse(raw, fallback={"topics": []})
    topics = result.get("topics", [])
    logger.info("Fetched %d topic suggestions", len(topics))
    return topics
