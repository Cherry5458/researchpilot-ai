# ─────────────────────────────────────────────────────────────────────────────
# services/orchestrator.py  –  Pipeline Orchestrator
# Wires all 8 agents together and yields status events (SSE-friendly).
# ─────────────────────────────────────────────────────────────────────────────

import logging
from typing import AsyncGenerator

from agents.agent1_validator import validate_topic
from agents.agent2_planner import create_research_plan
from agents.agent3_researcher import research_all_sections
from agents.agent4_analyst import analyze_research
from agents.agent5_writer import write_paper
from agents.agent6_reviewer import review_paper
from agents.agent7_citation import collect_all_sources, generate_citations
from agents.agent8_pdf import generate_pdf

logger = logging.getLogger(__name__)


async def run_pipeline(topic: str) -> tuple[bytes, dict]:
    """
    Execute the full 8-agent research pipeline.

    Args:
        topic: Raw user-supplied research topic.

    Returns:
        Tuple of (pdf_bytes, metadata_dict).

    Raises:
        ValueError: If the topic fails validation.
        Exception: Propagates any agent-level failure.
    """
    logger.info("=== Pipeline START: %s ===", topic)

    # ── Agent 1: Validate ────────────────────────────────────────────────────
    logger.info("Step 1/8 – Validating topic")
    validation = await validate_topic(topic)
    if not validation.get("is_valid", True):
        raise ValueError("Topic is too vague. Please be more specific.")
    validated_topic = validation["validated_topic"]
    keywords      = validation["keywords"]
    scope         = validation["research_scope"]

    # ── Agent 2: Plan ────────────────────────────────────────────────────────
    logger.info("Step 2/8 – Planning research")
    plan = await create_research_plan(validated_topic, keywords, scope)
    sections = plan["sections"]

    # ── Agent 3: Research ────────────────────────────────────────────────────
    logger.info("Step 3/8 – Researching sections")
    raw_research = await research_all_sections(validated_topic, keywords, sections)

    # ── Agent 4: Analyze ─────────────────────────────────────────────────────
    logger.info("Step 4/8 – Analyzing research")
    analyzed = await analyze_research(validated_topic, raw_research)

    # ── Agent 5: Write ───────────────────────────────────────────────────────
    logger.info("Step 5/8 – Writing paper")
    draft = await write_paper(validated_topic, analyzed, keywords, scope)

    # ── Agent 6: Review ──────────────────────────────────────────────────────
    logger.info("Step 6/8 – Reviewing paper")
    reviewed = await review_paper(draft)

    # ── Agent 7: Citations ───────────────────────────────────────────────────
    logger.info("Step 7/8 – Generating citations")
    raw_sources = collect_all_sources(raw_research)
    references  = await generate_citations(raw_sources)

    # ── Agent 8: PDF ─────────────────────────────────────────────────────────
    logger.info("Step 8/8 – Building PDF")
    pdf_bytes = generate_pdf(validated_topic, reviewed, references, keywords)

    metadata = {
        "validated_topic": validated_topic,
        "keywords": keywords,
        "word_count": len(reviewed.split()),
        "reference_count": len(references),
        "paper_text": reviewed,
        "references": references,
    }

    logger.info("=== Pipeline COMPLETE: %d words, %d refs ===",
                metadata["word_count"], metadata["reference_count"])
    return pdf_bytes, metadata
