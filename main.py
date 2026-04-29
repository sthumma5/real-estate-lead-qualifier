"""
Real Estate Lead Qualifier — CLI entry point.

Usage:
    python main.py --input data/sample_leads.csv
    python main.py --input leads.csv --output ranked.csv --workers 3
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

from qualifier.ai_engine import AIEngine
from qualifier.config import config
from qualifier.loader import load_leads
from qualifier.processor import process_leads, print_summary, save_results
from qualifier.utils import load_env

# ── Bootstrap ─────────────────────────────────────────────
load_env()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("qualifier.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lead-qualifier",
        description=f"{config.APP_NAME} v{config.APP_VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  python main.py --input data/sample_leads.csv
  python main.py --input leads.csv --output ranked.csv --workers 3
        """,
    )
    parser.add_argument("--input",   "-i", required=True,
                        help="Path to input CSV file")
    parser.add_argument("--output",  "-o", default=None,
                        help="Output CSV path (auto-generated if omitted)")
    parser.add_argument("--workers", "-w", type=int, default=config.DEFAULT_WORKERS,
                        help=f"Concurrent API workers (default: {config.DEFAULT_WORKERS})")
    return parser


def main() -> None:
    args    = build_parser().parse_args()
    infile  = args.input
    outfile = args.output or f"qualified_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    print(f"\n🏠  {config.APP_NAME} v{config.APP_VERSION}")
    print(f"    Input   : {infile}")
    print(f"    Output  : {outfile}")
    print(f"    Workers : {args.workers}\n")

    try:
        leads     = load_leads(infile)
        ai_engine = AIEngine()
    except FileNotFoundError as exc:
        logger.error(str(exc))
        sys.exit(1)
    except EnvironmentError as exc:
        logger.error(str(exc))
        sys.exit(1)

    qualified = process_leads(leads, ai_engine, max_workers=args.workers)
    save_results(qualified, outfile)
    print_summary(qualified)
    print(f"✅  Done — results saved to '{outfile}'\n")


if __name__ == "__main__":
    main()
