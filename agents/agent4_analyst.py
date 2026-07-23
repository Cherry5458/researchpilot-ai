# ─────────────────────────────────────────────────────────────────────────────
# agents/agent4_analyst.py  –  Analysis Agent
# Cleans, groups, and structures raw research data into a final paper outline.
# ─────────────────────────────────────────────────────────────────────────────

import json
import logging
from openai import AsyncOpenAI
from config import MODEL_NAME, OPENAI_API_KEY

logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
You are an expert academic analyst and editor.
You will receive raw research data (facts, statistics, findings) for multiple paper sections.

Your task:
1. Remove irrelevant or redundant information.
2. Group similar concepts together logically.
3. Enrich each section with analytical commentary (1-2 sentences explaining significance).
4. Produce a clean, structured outline ready for the academic writer.

Respond in this exact JSON format (no markdown):
{
  "sections": [
    {
      "section_title": "...",
      "synthesized_content": [
        "Analytical point 1 with supporting data.",
        "Analytical point 2 with supporting data.",
        "..."
      ],
      "analytical_note": "Brief note on why this content is significant."
    }
  ]
}
"""

async def analyze_research(topic: str, raw_research: list[dict]) -> dict:
    """
    Analyze and synthesize raw research data into a structured outline.

    Args:
        topic: Validated research topic.
        raw_research: List of research dicts from Agent 3.

    Returns:
        dict with 'sections' list of analyzed, structured content.
    """
    logger.info("Agent 4 – Analyzing research data (%d sections)", len(raw_research))

    # Compact serialization to stay within token limits
    serialized = json.dumps(raw_research, indent=None)

    user_content = f"Topic: {topic}\n\nRaw Research Data:\n{serialized}"

    response = await client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.3,
        max_tokens=2000,
    )

    raw = response.choices[0].message.content.strip()
    result: dict = json.loads(raw)
    logger.info("Agent 4 – Analysis complete: %d sections structured", len(result.get("sections", [])))
    return result
