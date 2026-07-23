# ─────────────────────────────────────────────────────────────────────────────
# utils/json_parser.py  –  Safe JSON parser for LLM responses
# Handles markdown fences, trailing commas, and broken JSON gracefully.
# ─────────────────────────────────────────────────────────────────────────────

import re
import json
import logging

logger = logging.getLogger(__name__)


def safe_parse(raw: str, fallback=None):
    """
    Robustly parse JSON from an LLM response.
    Handles: ```json fences, trailing commas, extra text before/after JSON.

    Args:
        raw: Raw LLM response string.
        fallback: Value to return if all parsing attempts fail.

    Returns:
        Parsed Python object, or fallback.
    """
    if not raw:
        return fallback

    # 1. Strip markdown code fences
    cleaned = re.sub(r"```(?:json)?", "", raw).replace("```", "").strip()

    # 2. Extract first JSON object or array
    match = re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', cleaned)
    if match:
        cleaned = match.group(1)

    # 3. Remove trailing commas before } or ]
    cleaned = re.sub(r',\s*([}\]])', r'\1', cleaned)

    # 4. Try parsing
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.warning("JSON parse failed after cleanup: %s", e)

    # 5. Last resort — return fallback
    logger.error("Could not parse JSON. Raw snippet: %s", raw[:300])
    return fallback
