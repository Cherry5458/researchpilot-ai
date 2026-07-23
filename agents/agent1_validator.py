# ─────────────────────────────────────────────────────────────────────────────
# agents/agent1_validator.py  –  Topic Validation Agent
# Validates the research topic, suggests improvements, and generates keywords.
# ─────────────────────────────────────────────────────────────────────────────

import logging
from openai import AsyncOpenAI
from config import MODEL_NAME, OPENAI_API_KEY
from utils.json_parser import safe_parse

logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
You are a research topic enhancement expert.
ALWAYS accept any topic. NEVER reject. ALWAYS set is_valid to true.
Just improve the topic slightly and generate keywords.

Respond ONLY in this exact JSON format (no markdown, no extra text):
{
  "is_valid": true,
  "validated_topic": "<improved topic title>",
  "keywords": ["kw1", "kw2", "kw3", "kw4", "kw5", "kw6"],
  "research_scope": "<2-3 sentence scope description>",
  "improvement_note": "None"
}
"""

async def validate_topic(raw_topic: str) -> dict:
    """
    Validate and enrich a raw research topic.

    Args:
        raw_topic: The user-supplied research topic string.

    Returns:
        dict with keys: is_valid, validated_topic, keywords, research_scope, improvement_note
    """
    logger.info("Agent 1 – Validating topic: %s", raw_topic)

    if len(raw_topic.strip()) < 5:
        return {
            "is_valid": False,
            "validated_topic": raw_topic,
            "keywords": [],
            "research_scope": "",
            "improvement_note": "Topic is too short. Please provide a descriptive research topic.",
        }

    response = await client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Research Topic: {raw_topic}"},
        ],
        temperature=0.3,
        max_tokens=512,
    )

    raw = response.choices[0].message.content.strip()
    result: dict = safe_parse(raw, fallback={
        "is_valid": True,
        "validated_topic": raw_topic,
        "keywords": [raw_topic],
        "research_scope": f"Research on {raw_topic}.",
        "improvement_note": "None",
    })
    logger.info("Agent 1 – Validation complete: %s", result.get("validated_topic"))
    return result
