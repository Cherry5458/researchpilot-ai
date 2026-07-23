# ─────────────────────────────────────────────────────────────────────────────
# agents/agent2_planner.py  –  Research Planning Agent
# Breaks the validated topic into logical academic sections with descriptions.
# ─────────────────────────────────────────────────────────────────────────────

import json
import logging
from openai import AsyncOpenAI
from config import MODEL_NAME, OPENAI_API_KEY

logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
You are an expert academic research planner.
Given a validated research topic, keywords, and scope, generate a structured research plan.

The plan must contain exactly these standard academic sections in order:
Abstract, Introduction, Literature Review, Methodology, Key Findings, Discussion, Future Scope, Conclusion, References

For each section provide:
- section_title: the section name
- objective: what this section must accomplish (1-2 sentences)
- key_points: 3-5 bullet points of what content to cover

Respond in this exact JSON format (no markdown):
{
  "sections": [
    {
      "section_title": "Abstract",
      "objective": "...",
      "key_points": ["point1", "point2", "point3"]
    }
  ]
}
"""

async def create_research_plan(validated_topic: str, keywords: list[str], scope: str) -> dict:
    """
    Create a structured academic research plan.

    Args:
        validated_topic: Cleaned topic title from Agent 1.
        keywords: List of research keywords from Agent 1.
        scope: Research scope description from Agent 1.

    Returns:
        dict with key 'sections' containing list of section plans.
    """
    logger.info("Agent 2 – Planning research for: %s", validated_topic)

    user_content = (
        f"Topic: {validated_topic}\n"
        f"Keywords: {', '.join(keywords)}\n"
        f"Scope: {scope}"
    )

    response = await client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.4,
        max_tokens=1200,
    )

    raw = response.choices[0].message.content.strip()
    result: dict = json.loads(raw)
    logger.info("Agent 2 – Plan created with %d sections", len(result.get("sections", [])))
    return result
