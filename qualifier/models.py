"""Data models for the lead qualifier."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Lead:
    """Represents one seller lead from the input CSV."""

    row_index:     int
    name:          str
    source:        str
    budget_min:    float
    budget_max:    float
    timeline:      str
    property_type: str
    location:      str
    motivation:    str
    contact_date:  str
    notes:         str = ""

    # Populated by AIEngine
    tier:        str            = ""
    score:       int            = 0
    reasoning:   str            = ""
    next_action: str            = ""
    error:       Optional[str]  = None

    @property
    def budget_display(self) -> str:
        return f"${self.budget_min:,.0f} – ${self.budget_max:,.0f}"

    @property
    def is_qualified(self) -> bool:
        return self.score > 0 and not self.error
