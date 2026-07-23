# ─────────────────────────────────────────────────────────────────────────────
# services/langgraph_orchestrator.py  –  LangGraph Pipeline
# Replaces the manual pipeline with a proper LangGraph DAG.
# Each agent is a node; edges define the flow.
# ─────────────────────────────────────────────────────────────────────────────

import logging
from typing import TypedDict, Any
from langgraph.graph import StateGraph, END

from agents.agent1_validator  import validate_topic
from agents.agent2_planner    import create_research_plan
from agents.agent3_researcher import research_all_sections
from agents.agent4_analyst    import analyze_research
from agents.agent5_writer     import write_paper
from agents.agent6_reviewer   import review_paper
from agents.agent7_citation   import collect_all_sources, generate_citations
from agents.agent8_pdf        import generate_pdf
from agents.agent9_plagiarism import check_plagiarism

logger = logging.getLogger(__name__)


# ── Shared state schema ───────────────────────────────────────────────────────
class ResearchState(TypedDict):
    # Inputs
    raw_topic:        str

    # Agent 1 outputs
    validated_topic:  str
    keywords:         list[str]
    scope:            str

    # Agent 2 outputs
    sections:         list[dict]

    # Agent 3 outputs
    raw_research:     list[dict]

    # Agent 4 outputs
    analyzed:         dict

    # Agent 5 outputs
    draft:            str

    # Agent 6 outputs
    reviewed:         str

    # Agent 7 outputs
    references:       list[str]

    # Agent 8 outputs
    pdf_bytes:        bytes

    # Agent 9 outputs
    plagiarism_report: dict

    # Error tracking
    error:            str


# ── Node functions (one per agent) ────────────────────────────────────────────

async def node_validate(state: ResearchState) -> ResearchState:
    logger.info("[LangGraph] Node 1: Validate")
    try:
        result = await validate_topic(state["raw_topic"])
        return {
            **state,
            "validated_topic": result["validated_topic"],
            "keywords":        result["keywords"],
            "scope":           result["research_scope"],
            "error":           "",
        }
    except Exception as e:
        return {**state, "error": f"Validation failed: {e}"}


async def node_plan(state: ResearchState) -> ResearchState:
    logger.info("[LangGraph] Node 2: Plan")
    try:
        plan = await create_research_plan(
            state["validated_topic"], state["keywords"], state["scope"]
        )
        return {**state, "sections": plan["sections"], "error": ""}
    except Exception as e:
        return {**state, "error": f"Planning failed: {e}"}


async def node_research(state: ResearchState) -> ResearchState:
    logger.info("[LangGraph] Node 3: Research")
    try:
        raw = await research_all_sections(
            state["validated_topic"], state["keywords"], state["sections"]
        )
        return {**state, "raw_research": raw, "error": ""}
    except Exception as e:
        return {**state, "error": f"Research failed: {e}"}


async def node_analyze(state: ResearchState) -> ResearchState:
    logger.info("[LangGraph] Node 4: Analyze")
    try:
        analyzed = await analyze_research(state["validated_topic"], state["raw_research"])
        return {**state, "analyzed": analyzed, "error": ""}
    except Exception as e:
        return {**state, "error": f"Analysis failed: {e}"}


async def node_write(state: ResearchState) -> ResearchState:
    logger.info("[LangGraph] Node 5: Write")
    try:
        draft = await write_paper(
            state["validated_topic"], state["analyzed"],
            state["keywords"], state["scope"]
        )
        return {**state, "draft": draft, "error": ""}
    except Exception as e:
        return {**state, "error": f"Writing failed: {e}"}


async def node_review(state: ResearchState) -> ResearchState:
    logger.info("[LangGraph] Node 6: Review")
    try:
        reviewed = await review_paper(state["draft"])
        return {**state, "reviewed": reviewed, "error": ""}
    except Exception as e:
        return {**state, "error": f"Review failed: {e}"}


async def node_citations(state: ResearchState) -> ResearchState:
    logger.info("[LangGraph] Node 7: Citations")
    try:
        raw_sources = collect_all_sources(state["raw_research"])
        references  = await generate_citations(raw_sources)
        return {**state, "references": references, "error": ""}
    except Exception as e:
        return {**state, "error": f"Citations failed: {e}"}


async def node_pdf(state: ResearchState) -> ResearchState:
    logger.info("[LangGraph] Node 8: PDF")
    try:
        pdf_bytes = generate_pdf(
            state["validated_topic"], state["reviewed"],
            state["references"], state["keywords"]
        )
        return {**state, "pdf_bytes": pdf_bytes, "error": ""}
    except Exception as e:
        return {**state, "error": f"PDF generation failed: {e}"}


async def node_plagiarism(state: ResearchState) -> ResearchState:
    logger.info("[LangGraph] Node 9: Plagiarism Check")
    try:
        result = await check_plagiarism(state["reviewed"])
        return {**state, "plagiarism_report": result, "error": ""}
    except Exception as e:
        logger.warning("Plagiarism check failed (non-fatal): %s", e)
        return {**state, "plagiarism_report": {}, "error": ""}


# ── Error router ──────────────────────────────────────────────────────────────
def should_continue(state: ResearchState) -> str:
    if state.get("error"):
        return "error"
    return "continue"


# ── Build the graph ───────────────────────────────────────────────────────────
def build_graph() -> Any:
    graph = StateGraph(ResearchState)

    # Add all nodes
    graph.add_node("validate",   node_validate)
    graph.add_node("plan",       node_plan)
    graph.add_node("research",   node_research)
    graph.add_node("analyze",    node_analyze)
    graph.add_node("write",      node_write)
    graph.add_node("review",     node_review)
    graph.add_node("citations",  node_citations)
    graph.add_node("pdf",        node_pdf)
    graph.add_node("plagiarism", node_plagiarism)

    # Entry point
    graph.set_entry_point("validate")

    # Sequential edges
    graph.add_edge("validate",   "plan")
    graph.add_edge("plan",       "research")
    graph.add_edge("research",   "analyze")
    graph.add_edge("analyze",    "write")
    graph.add_edge("write",      "review")
    graph.add_edge("review",     "citations")
    graph.add_edge("citations",  "pdf")
    graph.add_edge("pdf",        "plagiarism")
    graph.add_edge("plagiarism", END)

    return graph.compile()


# ── Main pipeline function ────────────────────────────────────────────────────
async def run_langgraph_pipeline(topic: str) -> tuple[bytes, dict]:
    """
    Run the full 9-node LangGraph pipeline.

    Args:
        topic: Raw user research topic.

    Returns:
        Tuple of (pdf_bytes, metadata_dict).
    """
    logger.info("=== LangGraph Pipeline START: %s ===", topic)

    app = build_graph()

    initial_state: ResearchState = {
        "raw_topic":       topic,
        "validated_topic": "",
        "keywords":        [],
        "scope":           "",
        "sections":        [],
        "raw_research":    [],
        "analyzed":        {},
        "draft":           "",
        "reviewed":        "",
        "references":      [],
        "pdf_bytes":       b"",
        "plagiarism_report": {},
        "error":           "",
    }

    final_state = await app.ainvoke(initial_state)

    if final_state.get("error"):
        raise Exception(final_state["error"])

    metadata = {
        "validated_topic":  final_state["validated_topic"],
        "keywords":         final_state["keywords"],
        "word_count":       len(final_state["reviewed"].split()),
        "reference_count":  len(final_state["references"]),
        "paper_text":       final_state["reviewed"],
        "references":       final_state["references"],
        "plagiarism":       final_state["plagiarism_report"],
    }

    logger.info("=== LangGraph Pipeline COMPLETE: %d words ===", metadata["word_count"])
    return final_state["pdf_bytes"], metadata
