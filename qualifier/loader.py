"""
CSV loader — validates input files and returns a list of Lead objects.
Pure I/O; no AI calls, no business logic.
"""

import logging
from pathlib import Path

import pandas as pd

from qualifier.config import REQUIRED_CSV_COLUMNS
from qualifier.models import Lead

logger = logging.getLogger(__name__)


def _parse_money(val: str) -> float:
    """'$120,000' → 120000.0"""
    try:
        return float(str(val).replace("$", "").replace(",", "").strip() or "0")
    except ValueError:
        return 0.0


def load_leads(filepath: str) -> list:
    """
    Load and validate a CSV of leads.

    Raises:
        FileNotFoundError: if the file does not exist.
        ValueError: if required columns are missing.

    Returns:
        List of Lead dataclasses.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: '{filepath}'")

    df = pd.read_csv(path)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    missing = REQUIRED_CSV_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing required columns: {sorted(missing)}")

    df = df.fillna("")

    leads = []
    for idx, row in df.iterrows():
        leads.append(Lead(
            row_index=int(idx),
            name=str(row["name"]).strip(),
            source=str(row["source"]).strip(),
            budget_min=_parse_money(row["budget_min"]),
            budget_max=_parse_money(row["budget_max"]),
            timeline=str(row["timeline"]).strip(),
            property_type=str(row["property_type"]).strip(),
            location=str(row["location"]).strip(),
            motivation=str(row["motivation"]).strip(),
            contact_date=str(row["contact_date"]).strip(),
            notes=str(row.get("notes", "")).strip(),
        ))

    logger.info("Loaded %d leads from '%s'", len(leads), filepath)
    return leads
