"""
Unit tests for the CSV loader.
Run with: pytest tests/
"""

import csv
import pytest
from pathlib import Path
from qualifier.loader import load_leads, _parse_money


# ── Money parser ──────────────────────────────────────────

def test_parse_money_plain():
    assert _parse_money("150000") == 150_000.0

def test_parse_money_with_dollar_and_commas():
    assert _parse_money("$150,000") == 150_000.0

def test_parse_money_empty():
    assert _parse_money("") == 0.0

def test_parse_money_invalid():
    assert _parse_money("N/A") == 0.0


# ── CSV loading ───────────────────────────────────────────

@pytest.fixture
def sample_csv(tmp_path):
    """Write a minimal valid CSV to a temp file."""
    p = tmp_path / "leads.csv"
    rows = [
        ["name","source","budget_min","budget_max","timeline","property_type","location","motivation","contact_date"],
        ["John Doe","Cold Call","100000","150000","30 days","Single Family","Tulsa OK","Divorce","2024-01-01"],
        ["Jane Smith","Referral","200000","250000","60 days","Multi-Family","Owasso OK","Retiring","2024-01-02"],
    ]
    with open(p, "w", newline="") as f:
        csv.writer(f).writerows(rows)
    return str(p)


def test_load_returns_correct_count(sample_csv):
    leads = load_leads(sample_csv)
    assert len(leads) == 2

def test_load_parses_name(sample_csv):
    leads = load_leads(sample_csv)
    assert leads[0].name == "John Doe"

def test_load_parses_budget(sample_csv):
    leads = load_leads(sample_csv)
    assert leads[0].budget_min == 100_000.0
    assert leads[0].budget_max == 150_000.0

def test_load_missing_column_raises(tmp_path):
    p = tmp_path / "bad.csv"
    p.write_text("name,source\nJohn,Cold Call\n")
    with pytest.raises(ValueError, match="missing required columns"):
        load_leads(str(p))

def test_load_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_leads("nonexistent_file.csv")
