# ─────────────────────────────────────────────────────────────────────────────
# config.py  –  Central configuration for ResearchPilot AI
# Change MODEL_NAME here to switch the LLM for every agent at once.
# ─────────────────────────────────────────────────────────────────────────────

import os
from dotenv import load_dotenv

load_dotenv()

# ── LLM ──────────────────────────────────────────────────────────────────────
MODEL_NAME: str = "gpt-4.1-mini"

# ── OpenAI ───────────────────────────────────────────────────────────────────
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

# ── Paper constraints ─────────────────────────────────────────────────────────
MIN_WORD_COUNT: int = 2500
MAX_RETRIES: int = 3

# ── CORS ──────────────────────────────────────────────────────────────────────
ALLOWED_ORIGINS: list[str] = ["*"]   # tighten in production
