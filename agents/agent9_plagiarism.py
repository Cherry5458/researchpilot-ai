# ─────────────────────────────────────────────────────────────────────────────
# agents/agent9_plagiarism.py  –  Plagiarism Checker Agent
# Analyses the paper for originality and returns a detailed score report.
# ─────────────────────────────────────────────────────────────────────────────

import logging
from openai import AsyncOpenAI
from config import MODEL_NAME, OPENAI_API_KEY
from utils.json_parser import safe_parse

logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
You are an expert academic plagiarism and originality checker.

You will receive a research paper text. Analyse it for:
1. Originality — how unique and original is the writing style and content?
2. Common Phrases — identify generic or commonly used academic phrases.
3. Repetition — identify repeated ideas within the paper.
4. Citation Coverage — are claims properly backed by citations [1], [2] etc?
5. Overall Originality Score — give a score from 0 to 100.

Scoring guide:
- 85-100: Highly original, publication ready
- 70-84:  Good, minor improvements needed
- 50-69:  Average, significant rewriting recommended
- Below 50: Poor originality

Respond ONLY in this exact JSON format (no markdown):
{
  "originality_score": 87,
  "grade": "Highly Original",
  "citation_coverage": "Good",
  "issues": [
    "Introduction contains some generic opening phrases.",
    "Conclusion repeats points from Discussion section."
  ],
  "strengths": [
    "Strong use of specific statistics throughout.",
    "Well-cited methodology section."
  ],
  "recommendation": "The paper demonstrates strong originality. Minor rewording of the introduction is suggested."
}
"""


async def check_plagiarism(paper_text: str) -> dict:
    """
    Analyse a paper for originality and return a detailed report.

    Args:
        paper_text: Full reviewed paper text.

    Returns:
        dict with originality_score, grade, issues, strengths, recommendation.
    """
    logger.info("Agent 9 – Running plagiarism/originality check")

    # Send only first 4000 words to stay within token limits
    words = paper_text.split()
    truncated = " ".join(words[:4000])

    response = await client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": f"Paper Text:\n{truncated}"},
        ],
        temperature=0.2,
        max_tokens=800,
    )

    raw = response.choices[0].message.content.strip()
    result = safe_parse(raw, fallback={
        "originality_score": 75,
        "grade": "Good",
        "citation_coverage": "Adequate",
        "issues": ["Could not fully analyse — paper may be too long."],
        "strengths": ["Paper was generated successfully."],
        "recommendation": "Review manually for originality.",
    })

    logger.info("Agent 9 – Originality score: %s%%", result.get("originality_score"))
    return result
