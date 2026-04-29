# 🏠 Real Estate Lead Qualifier

A Python CLI tool that batch-processes real estate seller leads using Claude AI. Reads a CSV of leads, scores each one as **Hot 🔥 / Warm ⚡ / Cold 🧊**, and outputs a ranked CSV with reasoning and next actions — replacing hours of manual review.

## What It Does

- Reads any CSV of seller leads (name, budget, timeline, motivation, etc.)
- Sends each lead to **Google Gemini AI** for scoring and qualification
- Processes all leads **concurrently** for speed (configurable workers)
- Outputs a ranked CSV sorted by tier and score
- Prints a live progress bar + console summary

## Demo

**Input (`sample_leads.csv`):**
```
name,source,budget_min,budget_max,timeline,motivation,...
John Martinez,Driving for Dollars,180000,220000,30-60 days,Divorce...
David Wilson,Driving for Dollars,50000,80000,Immediate,Tax delinquent...
...
```

**Output (`qualified_20240115_143022.csv`):**
```
Rank,Tier,Score,Name,Budget,Next Action,...
1,Hot 🔥,9,David Wilson,$50k–$80k,Call today — offer below ask...
2,Hot 🔥,8,John Martinez,$180k–$220k,Schedule walkthrough this week...
...
```

## Quick Start

**1. Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/lead-qualifier.git
cd lead-qualifier
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Set up your API key**
```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
```

**4. Run it**
```bash
# Using the sample leads provided
python lead_qualifier.py --input sample_leads.csv

# Custom output path and worker count
python lead_qualifier.py --input leads.csv --output ranked.csv --workers 3
```

## CSV Format

Your input CSV must have these columns (additional columns are ignored):

| Column | Description | Example |
|--------|-------------|---------|
| `name` | Seller name | John Martinez |
| `source` | How you found them | Driving for Dollars |
| `budget_min` | Minimum asking price | 180000 |
| `budget_max` | Maximum asking price | 220000 |
| `timeline` | How quickly they want to sell | 30-60 days |
| `property_type` | Type of property | Single Family |
| `location` | City/neighborhood | North Tulsa OK |
| `motivation` | Why they're selling | Divorce |
| `contact_date` | Date of first contact | 2024-01-15 |
| `notes` | *(optional)* Any extra context | Open to creative terms |

## CLI Options

```
python lead_qualifier.py [OPTIONS]

Options:
  --input,   -i   Path to input CSV file (required)
  --output,  -o   Output CSV path (default: qualified_TIMESTAMP.csv)
  --workers, -w   Concurrent API calls (default: 5)
```

## How Scoring Works

Claude evaluates each lead against three tiers:

- **Hot 🔥** — Motivated seller, realistic price, urgent timeline, strong acquisition fit
- **Warm ⚡** — Good potential but needs nurturing; longer or unclear timeline
- **Cold 🧊** — Low urgency, unrealistic price, poor fit, or no real motivation

Each lead also gets a score from 1–10, a 2–3 sentence reasoning, and a specific next action.

## Tech Stack

- **Language:** Python 3.10+
- **AI:** Google Gemini API (free tier)
- **Data:** pandas
- **UX:** tqdm progress bar
- **Concurrency:** ThreadPoolExecutor

## License

MIT
