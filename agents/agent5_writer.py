# ─────────────────────────────────────────────────────────────────────────────
# agents/agent5_writer.py  –  Academic Writer Agent
# Generates a full, professional academic paper (min 2500 words).
# ─────────────────────────────────────────────────────────────────────────────

import logging
from datetime import date
from openai import AsyncOpenAI
from config import MODEL_NAME, OPENAI_API_KEY, MIN_WORD_COUNT

logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = f"""
You are a professional academic writer with expertise in writing high-quality research papers.

Write a complete academic research paper based on the structured outline provided.

Requirements:
- Minimum {MIN_WORD_COUNT} words total.
- Include all sections: Abstract, Introduction, Literature Review, Methodology, Key Findings, Discussion, Future Scope, Conclusion.
- Use formal, academic English. No colloquialisms.
- No repetition of ideas across sections.
- Each section must flow naturally into the next with transition sentences.
- Use paragraph form — no bullet points in the paper body.
- Include specific data, statistics, and named examples where available.
- Write as if submitting to an academic journal.

IMPORTANT — INLINE CITATIONS:
- Every factual claim, statistic, or finding MUST have an inline citation marker like [1], [2], [3] etc.
- Place the citation number in square brackets immediately after the relevant sentence or fact.
- Use numbers 1 through 10 for citations (they will be mapped to real references later).
- Example: "Artificial intelligence has transformed modern healthcare significantly [1]. Studies show a 40%% improvement in diagnostic accuracy [2]."
- Every paragraph must contain at least 2-3 citation markers.

Format your response as plain text with section headers marked like:
## Abstract
<content>

## Introduction
<content>

... and so on for all sections.

Do NOT include a References section — that is handled separately.
"""

async def write_paper(
    topic: str,
    analyzed_outline: dict,
    keywords: list[str],
    scope: str,
) -> str:
    """
    Generate the full academic paper text.

    Args:
        topic: Validated research topic.
        analyzed_outline: Structured outline from Agent 4.
        keywords: Research keywords.
        scope: Research scope.

    Returns:
        Full paper text as a string with ## section headers.
    """
    logger.info("Agent 5 – Writing academic paper for: %s", topic)

    today = date.today().strftime("%B %d, %Y")
    sections_text = ""
    for sec in analyzed_outline.get("sections", []):
        sections_text += f"\n\nSection: {sec['section_title']}\n"
        sections_text += "\n".join(f"- {pt}" for pt in sec.get("synthesized_content", []))
        sections_text += f"\nNote: {sec.get('analytical_note', '')}"

    user_content = (
        f"Paper Title: {topic}\n"
        f"Date: {today}\n"
        f"Keywords: {', '.join(keywords)}\n"
        f"Scope: {scope}\n"
        f"\nStructured Outline:{sections_text}"
    )

    response = await client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.6,
        max_tokens=4096,
    )

    paper_text: str = response.choices[0].message.content.strip()
    word_count = len(paper_text.split())
    logger.info("Agent 5 – Paper written: %d words", word_count)
    return paper_text
