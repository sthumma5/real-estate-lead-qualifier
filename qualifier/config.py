"""Central configuration for the Lead Qualifier."""

from dataclasses import dataclass


@dataclass(frozen=True)
class QualifierConfig:
    # App
    APP_NAME: str    = "Real Estate Lead Qualifier"
    APP_VERSION: str = "1.0.0"

    # AI
    AI_MODEL: str         = "llama-3.1-8b-instant"
    AI_MAX_TOKENS: int    = 350
    AI_TEMPERATURE: float = 0.2

    # Processing
    DEFAULT_WORKERS: int  = 3
    RETRY_ATTEMPTS: int   = 3
    RETRY_WAIT_BASE: int  = 15   # seconds; multiplied by attempt number

    # Tier labels
    TIER_HOT:  str = "Hot 🔥"
    TIER_WARM: str = "Warm ⚡"
    TIER_COLD: str = "Cold 🧊"


config = QualifierConfig()

TIER_ORDER = {
    config.TIER_HOT:  0,
    config.TIER_WARM: 1,
    config.TIER_COLD: 2,
}

REQUIRED_CSV_COLUMNS = {
    "name", "source", "budget_min", "budget_max",
    "timeline", "property_type", "location", "motivation", "contact_date",
}
