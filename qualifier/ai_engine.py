"""
AI Engine — wraps Groq API calls for lead qualification.
Isolated from CSV I/O and CLI; swappable for any LLM provider.
"""

import logging
import os

from groq import Groq

from qualifier.config import config
from qualifier.models import Lead

logger = logging.getLogger(__name__)

_PROMPT_TEMPLATE = """You are a senior acquisitions analyst at a $100M real estate investment firm.
Evaluate this seller lead and determine acquisition priority.

LEAD:
- Name:            {name}
- Source:          {source}
- Budget:          {budget}
- Timeline:        {timeline}
- Property Type:   {property_type}
- Location:        {location}
- Motivation:      {motivation}
- First Contact:   {contact_date}
{notes_line}

TIERS:
• Hot 🔥  — Motivated seller, realistic price, urgent timeline, strong fit
• Warm ⚡ — Good potential, minor concerns, longer or unclear timeline
• Cold 🧊 — Low urgency, unrealistic price, poor fit, or no motivation

Reply in EXACTLY this format (no extra text):
TIER: [Hot 🔥 / Warm ⚡ / Cold 🧊]
SCORE: [1-10]
REASONING: [2–3 sentences: tier rationale, key strengths, red flags]
NEXT_ACTION: [One specific next step — call, email, schedule visit, pass, revisit MM/DD, etc.]"""


class AIEngine:
    """Handles all LLM communication for lead qualification."""

    def __init__(self, api_key: str | None = None):
        key = api_key or os.getenv("GROQ_API_KEY")
        if not key:
            raise EnvironmentError("GROQ_API_KEY is not set.")
        self._client = Groq(api_key=key)

    def qualify(self, lead: Lead) -> Lead:
        """
        Score a lead and return it populated with tier / score / reasoning.
        Mutates the lead in-place and returns it for chaining.
        """
        prompt = _PROMPT_TEMPLATE.format(
            name=lead.name,
            source=lead.source,
            budget=lead.budget_display,
            timeline=lead.timeline,
            property_type=lead.property_type,
            location=lead.location,
            motivation=lead.motivation,
            contact_date=lead.contact_date,
            notes_line=f"- Notes: {lead.notes}" if lead.notes else "",
        )

        try:
            response = self._client.chat.completions.create(
                model=config.AI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=config.AI_MAX_TOKENS,
                temperature=config.AI_TEMPERATURE,
            )
            self._parse_into(lead, response.choices[0].message.content)
        except Exception as exc:
            logger.error("AIEngine.qualify failed for '%s': %s", lead.name, exc)
            lead.tier  = config.TIER_COLD
            lead.score = 0
            lead.error = str(exc)

        return lead

    @staticmethod
    def _normalize_tier(raw: str) -> str:
        """Normalize any tier variant the LLM returns to our canonical format."""
        lower = raw.lower()
        if "hot" in lower or raw.strip() in ("🔥", "🔥 Hot", "Hot", "hot"):
            return config.TIER_HOT
        if "warm" in lower or "⚡" in raw:
            return config.TIER_WARM
        return config.TIER_COLD

    @staticmethod
    def _parse_into(lead: Lead, text: str) -> None:
        """Parse structured LLM response into the lead object."""
        for line in text.strip().splitlines():
            if ":" not in line:
                continue
            key, _, val = line.partition(":")
            key, val = key.strip().upper(), val.strip()
            if key == "TIER":
                lead.tier = AIEngine._normalize_tier(val)
            elif key == "SCORE":
                try:
                    lead.score = max(1, min(10, int(val)))
                except ValueError:
                    pass
            elif key == "REASONING":
                lead.reasoning = val
            elif key == "NEXT_ACTION":
                lead.next_action = val
