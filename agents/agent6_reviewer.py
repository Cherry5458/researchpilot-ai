# ─────────────────────────────────────────────────────────────────────────────
# agents/agent6_reviewer.py  –  Reviewer Agent
# Reviews and improves grammar, flow, transitions, and readability.
# ─────────────────────────────────────────────────────────────────────────────

import logging
from openai import AsyncOpenAI
from config import MODEL_NAME, OPENAI_API_KEY

logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
You are a senior academic editor and peer reviewer.

You will receive a draft academic research paper. Your task is to:
1. Fix all grammar and punctuation errors.
2. Improve sentence flow and readability.
3. Remove any repetition of ideas.
4. Add or improve transition sentences between paragraphs and sections.
5. Ensure consistent academic tone throughout.
6. Strengthen weak or vague sentences with more precise language.

CRITICAL RULES:
- Preserve ALL inline citation markers like [1], [2], [3] exactly where they are.
- NEVER remove or move citation markers — they must stay at the end of the sentence they belong to.
- If a sentence has no citation and states a fact, ADD a citation marker like [3] or [4].
- Preserve all ## section headers exactly as written.
- Do NOT add or remove sections.
- Do NOT shorten the paper — maintain or expand length.
- Return only the improved paper text. No commentary, no preamble.
"""

async def review_paper(draft_paper: str) -> str:
    """
    Review and improve the draft academic paper.

    Args:
        draft_paper: Full paper text from Agent 5.

    Returns:
        Improved paper text as a string.
    """
    logger.info("Agent 6 – Reviewing paper (%d words)", len(draft_paper.split()))

    response = await client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": draft_paper},
        ],
        temperature=0.3,
        max_tokens=4096,
    )

    reviewed: str = response.choices[0].message.content.strip()
    logger.info("Agent 6 – Review complete (%d words)", len(reviewed.split()))
    return reviewed
