"""
Batch processor — concurrent lead qualification with progress tracking.
Orchestrates AIEngine calls across a list of leads.
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
from tqdm import tqdm

from qualifier.ai_engine import AIEngine
from qualifier.config import config, TIER_ORDER
from qualifier.models import Lead

logger = logging.getLogger(__name__)


def process_leads(leads: list, ai_engine: AIEngine, max_workers: int = config.DEFAULT_WORKERS) -> list:
    """
    Qualify all leads concurrently with a live progress bar.

    Returns:
        Sorted list of Lead objects: Hot → Warm → Cold, then by score desc.
    """
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_qualify_with_retry, lead, ai_engine): lead
            for lead in leads
        }

        with tqdm(
            total=len(leads),
            desc="Qualifying leads",
            unit="lead",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]",
        ) as pbar:
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                pbar.set_postfix({
                    "🔥": sum(1 for r in results if "Hot"  in r.tier),
                    "⚡": sum(1 for r in results if "Warm" in r.tier),
                    "🧊": sum(1 for r in results if "Cold" in r.tier),
                })
                pbar.update(1)

    results.sort(key=lambda x: (TIER_ORDER.get(x.tier, 3), -x.score))
    return results


def _qualify_with_retry(lead: Lead, engine: AIEngine) -> Lead:
    """Qualify a single lead, retrying on rate-limit errors."""
    for attempt in range(1, config.RETRY_ATTEMPTS + 1):
        try:
            return engine.qualify(lead)
        except Exception as exc:
            if "429" in str(exc) and attempt < config.RETRY_ATTEMPTS:
                wait = config.RETRY_WAIT_BASE * attempt
                logger.warning(
                    "Rate limit for '%s'. Retrying in %ds (attempt %d/%d)…",
                    lead.name, wait, attempt, config.RETRY_ATTEMPTS,
                )
                time.sleep(wait)
            else:
                lead.error = str(exc)
                lead.tier  = config.TIER_COLD
                return lead
    return lead


def save_results(leads: list, output_path: str) -> None:
    """Write ranked results to CSV."""
    rows = [{
        "Rank":          rank,
        "Tier":          lead.tier,
        "Score":         lead.score,
        "Name":          lead.name,
        "Source":        lead.source,
        "Budget":        lead.budget_display,
        "Timeline":      lead.timeline,
        "Property Type": lead.property_type,
        "Location":      lead.location,
        "Motivation":    lead.motivation,
        "Contact Date":  lead.contact_date,
        "AI Reasoning":  lead.reasoning,
        "Next Action":   lead.next_action,
        "Notes":         lead.notes,
        "Error":         lead.error or "",
    } for rank, lead in enumerate(leads, start=1)]

    pd.DataFrame(rows).to_csv(output_path, index=False, encoding="utf-8")
    logger.info("Saved %d results → '%s'", len(rows), output_path)


def print_summary(leads: list) -> None:
    """Print a formatted console summary."""
    hot  = [l for l in leads if "Hot"  in l.tier]
    warm = [l for l in leads if "Warm" in l.tier]
    cold = [l for l in leads if "Cold" in l.tier]

    print("\n" + "═" * 62)
    print(f"   {config.APP_NAME.upper()}")
    print("═" * 62)
    print(f"   Total  : {len(leads)}")
    print(f"   🔥 Hot  : {len(hot)}")
    print(f"   ⚡ Warm : {len(warm)}")
    print(f"   🧊 Cold : {len(cold)}")
    print("═" * 62)

    if hot:
        print("\n🔥  HOT LEADS — CONTACT IMMEDIATELY\n")
        for lead in hot:
            rank = leads.index(lead) + 1
            print(f"  #{rank:02d}  {lead.name:<25}  Score: {lead.score}/10")
            print(f"       {lead.budget_display}  |  {lead.location}")
            print(f"       → {lead.next_action}\n")

    print("═" * 62 + "\n")
