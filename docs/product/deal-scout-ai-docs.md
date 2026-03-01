# Deal Scout AI — Product Documentation Suite
> **Version:** 1.0 | **Owner:** Ablo | **Zip Focus:** 77304 (Conroe, TX) | **Status:** Discovery

---

## Table of Contents
1. [Product Vision](#1-product-vision)
2. [Persona — The Optimized Tech Lead](#2-persona)
3. [User Story Map](#3-user-story-map)
4. [Technical Architecture & Guide](#4-technical-architecture)

---

# 1. PRODUCT VISION

## Vision Statement

> **Deal Scout AI** is a personal shopping agent that works while you sleep — autonomously scanning retailers, extracting deal intelligence, and calculating the *true* cost of ownership so you never overpay or miss a time-limited perk again.

## The Problem It Solves

Manual deal-hunting is an invisible tax on high-performers. Checking Best Buy, Samsung.com, Costco, and carrier sites daily to catch a $200 trade-in bonus or a free Galaxy Buds 4 bundle is a 30–45 minute ritual that compounds into real lost hours per month — with no guarantee you caught the best window.

The market does not lack deal aggregators. It lacks a **personalized, location-aware, TCO-calculating agent** that understands *your* device ecosystem, *your* zip code's pickup availability, and *your* carrier relationship.

## Why Not What Already Exists?

| Tool | Gap |
|------|-----|
| Google Shopping | No TCO. No trade-in intelligence. No local pickup validation. |
| Honey / Capital One Shopping | Coupon-layer only. No agentic scheduling. No carrier deals. |
| Slickdeals | Manual community posts. No personalization. No local context. |
| CamelCamelCamel | Amazon only. Passive. No action layer. |

**Deal Scout AI** is the first layer *above* these — an orchestration agent that calls into them, synthesizes, and acts.

## Total Cost of Ownership (TCO) Engine

The core intellectual property of Deal Scout AI is its TCO calculator. For a device like the Samsung Galaxy S26 Ultra, a raw price comparison ($1,299 vs $1,199) is meaningless without the full picture.

**TCO Formula:**

```
TCO = Base Price
    − Trade-In Value (carrier + Samsung direct, whichever is higher)
    − Reserve/Pre-Order Credits (e.g., Samsung $30 reserve credit)
    − Bundle Value (e.g., Galaxy Buds 4 @ $149 MSRP → assign % of value)
    − Financing Arbitrage (0% APR 24mo vs. investing lump sum at 5.5% APY)
    + Tax (Conroe, TX: 8.25%)
    + Shipping vs. Local Pickup delta (time + gas cost at 77304)
    ──────────────────────────────────────────────
    = TRUE NET COST
```

**Example Output — Samsung Galaxy S26 Ultra (projected):**

| Source | Base Price | Trade-In (S24U) | Perks | Tax | TCO |
|--------|-----------|-----------------|-------|-----|-----|
| Samsung.com | $1,299 | −$700 | −$30 reserve, −$149 Buds | +$107 | **$527** |
| Best Buy | $1,299 | −$650 | None | +$107 | **$756** |
| AT&T (77304) | $0 down | −$800 (36mo) | None | Spread | **$499** (lock-in risk) |

> **Agent Decision:** Samsung.com wins on TCO if you value Buds at 70%+ of MSRP and can pick up at Conroe Best Buy for same-day.

## Smallest Valuable Version (MVP)

One device. One zip. One daily digest email/notification with ranked TCO comparison. That's it. No app. No dashboard. Just a scheduled agent that sends you an intelligence brief every morning by 7 AM CT.

## Market Sizing

- US consumers actively researching flagship smartphones: ~12M/year
- Willing to pay for automated deal intelligence (proxy: Honey Premium, subscription deal sites): ~8–12% → ~1M TAM
- Beachhead: Tech-forward professionals in suburban TX, FL, GA metros — estimated 80K–120K addressable users at $9–19/mo = **$9–27M ARR potential**

---

# 2. PERSONA

## Primary Persona — "The Optimized Tech Lead"

```
┌─────────────────────────────────────────────────────────┐
│  NAME:     Marcus A. (modeled archetype)                │
│  ROLE:     Senior Technical Program Manager / Scrum Lead│
│  LOCATION: Conroe, TX 77304                             │
│  INCOME:   $150K–$200K HHI                              │
│  DEVICES:  Samsung Galaxy S24 Ultra, Windows + Linux    │
│  TOOLS:    Claude AI, Cursor, Docker, Ollama            │
└─────────────────────────────────────────────────────────┘
```

### Goals
- Own the best available flagship device with the **lowest net spend**, not necessarily the lowest sticker price.
- **Never miss a time-limited window** — Samsung reserve credits, carrier promos, and bundle deals have hard expiration dates he currently tracks manually.
- Automate low-value repetitive tasks (daily price checks) so cognitive bandwidth goes to high-leverage work (AI development, product strategy, client delivery).

### Frustrations
- Checks Samsung.com, Best Buy, and Costco manually 3–4x/week. Has missed at least one major promo ($200 Samsung upgrade bonus in 2023) because he checked 2 days after it expired.
- Best Buy's local inventory for 77304 is inconsistent — online says "available" but the Conroe location doesn't stock the 512GB Titanium Black until a week later.
- Trade-in calculators across carriers and Samsung.com return different values for the same device — manual reconciliation is error-prone.

### Behaviors
- High trust in AI-assisted automation. Already uses Claude Code and Cursor for dev work — comfortable delegating research tasks to agentic workflows.
- Prefers a **morning brief** (6–7 AM CT) before the workday starts. Mobile notification is acceptable; email digest is preferred for archiving.
- Uses Revolut and Amex for purchases — values cashback and financing arbitrage (Revolut 5.5% APY means 0% APR financing has measurable value).

### Willingness to Pay
- **$15–$25/month** for a service that demonstrably saves $200+ per device cycle (proven by TCO report).
- Would pay a one-time $50 for a "deal alert" on a specific SKU + zip with a 30-day window.

### Quote (synthesized)
> *"I don't want to check Best Buy every morning. I want an agent that does it and tells me: 'Today is the day to pull the trigger — here's exactly why.'"*

---

## Anti-Persona — "The Casual Bargain Hunter"

```
NAME:     Sandra
PROFILE:  Replaces phone every 3–4 years, not annually
BEHAVIOR: Asks Facebook groups for deal advice
PAIN:     Wants "cheap," not "optimized"
WHY NOT:  Won't pay $15/mo for automation. Finds the complexity overwhelming.
          This is NOT our user.
```

> **PM Note:** Resisting the temptation to build for Sandra will be the hardest ongoing discipline. Feature requests will come in for "simpler" or "cheaper" — stay anchored to Marcus.

---

# 3. USER STORY MAP

## Epic Overview

```
BACKBONE (Activities):
────────────────────────────────────────────────────────────────────────────
[1. Config]  [2. Daily Scan]  [3. AI Extraction]  [4. TCO Calc]  [5. Alert]
────────────────────────────────────────────────────────────────────────────

FUTURE BACKBONE:
────────────────────────────────────────────────
[6. Travel Logistics — Delta Flight Tracking]
────────────────────────────────────────────────
```

---

## EPIC 1 — Daily Automated Research

**Goal:** Agent runs every 24 hours without human intervention.

| Story ID | User Story | Acceptance Criteria | MVP? |
|----------|-----------|---------------------|------|
| R-01 | As Marcus, I want the agent to run every day at 5 AM CT so I get results before my workday. | Cron/scheduler triggers at 05:00 CT ±2 min. Verified via logs. | ✅ |
| R-02 | As Marcus, I want to configure which SKUs to track (starting: Galaxy S26 Ultra, 512GB, all colors). | Config file or .env with SKU list. Agent reads before each run. | ✅ |
| R-03 | As Marcus, I want the agent to target my zip code (77304) so local pickup availability is always included. | All retailer queries pass `zip=77304`. Pickup flag returned per result. | ✅ |
| R-04 | As Marcus, I want the agent to self-heal if one source is down, so the run doesn't fail entirely. | Try/catch per source. Partial results still delivered. Error logged. | ✅ |
| R-05 | As Marcus, I want a run history so I can see price trends over time. | SQLite or JSON log stores each run's raw results with timestamp. | ⬜ Post-MVP |

---

## EPIC 2 — AI Data Extraction

**Goal:** Convert unstructured retailer HTML/JSON into structured deal objects.

| Story ID | User Story | Acceptance Criteria | MVP? |
|----------|-----------|---------------------|------|
| E-01 | As the system, I need to extract base price, trade-in offer, and bundle perks from Samsung.com for the target SKU. | Structured JSON output: `{price, trade_in, perks[], pickup_available, url, timestamp}` | ✅ |
| E-02 | As the system, I need to extract equivalent data from BestBuy.com for 77304. | Same schema as E-01. Pickup confirmed via Best Buy store locator API or scraper. | ✅ |
| E-03 | As the system, I need to extract carrier deals (AT&T, T-Mobile, Verizon) including installment structure. | Schema extended: `{monthly_payment, term_months, lock_in_penalty, effective_price}` | ⬜ V2 |
| E-04 | As the system, I need an AI parser (LLM call) to handle DOM changes gracefully. | If CSS selector fails, fall back to LLM-based HTML parsing. Accuracy >90% on test set. | ✅ |
| E-05 | As Marcus, I want the agent to detect time-limited deals (e.g., "Offer ends Sunday") and flag urgency. | Regex + LLM extracts deadline. `urgent: true` flag added if deadline ≤ 72 hours. | ✅ |

---

## EPIC 3 — Price Comparison & TCO Calculation

**Goal:** Rank all sources by true net cost, not sticker price.

| Story ID | User Story | Acceptance Criteria | MVP? |
|----------|-----------|---------------------|------|
| C-01 | As Marcus, I want a TCO score for each source so I can see the real cost at a glance. | TCO formula applied (see Vision section). Output: ranked table, lowest TCO first. | ✅ |
| C-02 | As Marcus, I want trade-in values automatically compared across sources so I get the best trade-in without manual research. | Agent queries Samsung Trade-In + Best Buy Trade-In APIs. Best value surfaced. | ✅ |
| C-03 | As Marcus, I want financing arbitrage calculated using my Revolut savings rate (5.5% APY) so I know if 0% APR has real value. | Input: `savings_apy=5.5%`. Output: `financing_benefit = principal × apy × term`. | ⬜ V2 |
| C-04 | As Marcus, I want bundle perks assigned a monetary value (e.g., Galaxy Buds 4 = $149 MSRP × 70% = $104 credit). | Configurable perk valuation multiplier (default 70%). Adjustable in config. | ✅ |
| C-05 | As Marcus, I want Conroe, TX tax (8.25%) automatically applied so TCO is always after-tax. | Tax rate in config. Applied to all non-tax-exempt transactions. | ✅ |

---

## EPIC 4 — Notification & Digest

**Goal:** Deliver actionable intelligence, not raw data.

| Story ID | User Story | Acceptance Criteria | MVP? |
|----------|-----------|---------------------|------|
| N-01 | As Marcus, I want a daily email digest by 6 AM CT with ranked TCO comparison and a clear recommended action. | SendGrid/Resend email sent ≤ 6 AM CT. Subject: `[Deal Scout] S26 Ultra — Best deal today: $527 TCO`. | ✅ |
| N-02 | As Marcus, I want a "pull trigger today" flag if TCO is at a 30-day low, so I know when to actually buy. | Agent compares today's best TCO to 30-day log. If lowest, badge added to email. | ✅ |
| N-03 | As Marcus, I want a push notification (iOS/Android) for urgent deals with <72h window. | Pushover or ntfy.sh notification. Triggered by `urgent: true` flag. | ⬜ V1.5 |
| N-04 | As Marcus, I want to reply "BUY" to the email and have the agent save the deal to a purchase log. | Email reply parsing via webhook. Saves deal to `purchases.json` with timestamp. | ⬜ V2 |

---

## EPIC 5 (FUTURE) — Travel Logistics: Delta Flight Tracking

**Goal:** Extend the agent to track Delta flights relevant to Marcus's travel patterns (e.g., IAH → ATL, IAH → SEA).

> **PM Checkpoint:** Do not build this until Epic 1–4 are proven and generating value. The core agent architecture will support this extension naturally — it's the same scrape → extract → compare → notify loop applied to flight pricing.

| Story ID | User Story | Acceptance Criteria | MVP of Epic? |
|----------|-----------|---------------------|------|
| T-01 | As Marcus, I want to track specific routes (IAH → ATL) for price drops below a threshold I set. | Config: `{route, threshold_price, travel_window}`. Alert if price drops below threshold. | ✅ |
| T-02 | As Marcus, I want Delta SkyMiles redemption value calculated alongside cash price so I can make the right call. | Input: `skymiles_balance`. Output: `cpp (cents per point)` vs cash price. Flag if CPP > 1.5¢. | ✅ |
| T-03 | As Marcus, I want Basic Economy vs Main Cabin TCO compared, including bag fees and seat selection. | Fee schedule hardcoded (updatable). True cost comparison in digest. | ⬜ V2 |
| T-04 | As Marcus, I want Amex Delta Reserve benefits factored in (companion certificate, upgraded boarding). | Config: `amex_delta_reserve: true`. Calculates annual benefit allocation per trip. | ⬜ V2 |

---

## MVP Cutline Summary

```
✅ IN MVP (Week 1–3):
  R-01, R-02, R-03, R-04
  E-01, E-02, E-04, E-05
  C-01, C-02, C-04, C-05
  N-01, N-02

⬜ POST-MVP (V1.5–V2):
  R-05, E-03, C-03, N-03, N-04
  All of Epic 5 (Travel Logistics)
```

**MVP Success Metric:** Agent runs daily for 14 consecutive days without manual intervention AND delivers at least one actionable deal insight that Marcus would not have found manually. TCO accuracy within ±5% of manually calculated value.

---

# 4. TECHNICAL ARCHITECTURE & GUIDE

## Stack Recommendation — Optimized for Cursor + Claude Code + Gemini

Given your current setup (Cursor IDE, Claude Code, Gemini access, Linux + Nvidia RTX 30 series, Ollama local), here is the architecture designed to leverage what you already have.

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     DEAL SCOUT AI — SYSTEM                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐    ┌───────────────┐    ┌─────────────────────┐  │
│  │  CRON    │───▶│  Orchestrator │───▶│  Source Scrapers    │  │
│  │ (5AM CT) │    │  (Python)     │    │  Samsung / BestBuy  │  │
│  └──────────┘    └──────┬────────┘    └──────────┬──────────┘  │
│                         │                         │             │
│                         ▼                         ▼             │
│                  ┌─────────────┐         ┌────────────────┐     │
│                  │  AI Parser  │         │  Raw HTML/JSON │     │
│                  │ Claude API  │◀────────│  Cache (Redis/ │     │
│                  │ or Gemini   │         │  flat file)    │     │
│                  └──────┬──────┘         └────────────────┘     │
│                         │                                       │
│                         ▼                                       │
│                  ┌─────────────┐                                │
│                  │  TCO Engine │                                │
│                  │  (Python)   │                                │
│                  └──────┬──────┘                                │
│                         │                                       │
│                         ▼                                       │
│                  ┌─────────────┐    ┌────────────────────────┐  │
│                  │  Deal Store │    │  Notification Layer    │  │
│                  │  (SQLite)   │───▶│  Email (Resend) +      │  │
│                  └─────────────┘    │  Push (ntfy.sh)        │  │
│                                     └────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### 1. Orchestrator (Python — `orchestrator.py`)

The central runner. Invoked by cron. Calls each scraper, passes results to AI Parser, feeds into TCO Engine, writes to Deal Store, triggers notifications.

**Why Python?** Claude Code and Cursor are both exceptional at Python generation and debugging. Your ML background means the async patterns are familiar. No overhead of a Node runtime.

```python
# orchestrator.py — skeleton (Claude Code will flesh this out)
import asyncio
from scrapers import samsung, bestbuy
from ai_parser import parse_deal
from tco_engine import calculate_tco
from notifier import send_digest

async def run():
    raw_deals = await asyncio.gather(
        samsung.fetch(sku="S26-Ultra", zip="77304"),
        bestbuy.fetch(sku="S26-Ultra", zip="77304"),
    )
    parsed = [parse_deal(d) for d in raw_deals]
    scored = [calculate_tco(p) for p in parsed]
    ranked = sorted(scored, key=lambda x: x["tco"])
    await send_digest(ranked)

if __name__ == "__main__":
    asyncio.run(run())
```

---

### 2. Source Scrapers (`scrapers/`)

**Tool:** Playwright (headless Chromium) over BeautifulSoup. Samsung and Best Buy render prices client-side via JavaScript — static scrapers will miss dynamic pricing.

```bash
pip install playwright
playwright install chromium
```

**Cursor Prompt to generate scrapers:**
> *"Write a Playwright scraper in Python for samsung.com/us/smartphones that extracts base price, trade-in value for Galaxy S24 Ultra, bundle perks, and reserve credit for the S26 Ultra 512GB. Return a typed dataclass. Handle `StaleElementReferenceException` gracefully."*

**Best Buy Local Pickup Validation:** Use Best Buy's public availability API (no auth required):
```
GET https://www.bestbuy.com/api/3.0/priceBlocks?skuId={SKU_ID}&storeId={STORE_ID}
```
Find the Conroe Best Buy store ID once (it's stable) and hardcode it in config.

---

### 3. AI Parser (`ai_parser.py`)

**Primary:** Claude API (claude-sonnet-4-6 via Anthropic API — you have access).
**Fallback:** Gemini 2.0 Flash (Google AI Studio — fast, cheap for high-volume parsing).
**Local fallback:** Ollama + `llama3.1:8b` on your RTX 30 series for offline runs.

**Usage pattern:** Only invoke AI parser when CSS selectors fail (DOM change detected). This keeps API costs near zero on stable days.

```python
# ai_parser.py
import anthropic

client = anthropic.Anthropic()

PARSE_PROMPT = """
Extract the following from this Samsung product page HTML:
- base_price (float, USD)
- trade_in_value (float, USD, for Galaxy S24 Ultra)
- perks (list of strings, e.g. ["Galaxy Buds 4", "$30 reserve credit"])
- pickup_available (bool, for zip 77304)

Return ONLY valid JSON. No explanation.

HTML:
{html}
"""

def parse_deal(html: str) -> dict:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": PARSE_PROMPT.format(html=html[:15000])}]
    )
    return json.loads(response.content[0].text)
```

**When to use Gemini instead:** For high-frequency parsing tasks where you want to preserve Anthropic API credits. Gemini 2.0 Flash is fast and accurate enough for structured extraction. Use Claude for reasoning tasks (TCO narrative, deal recommendation copy).

**When to use Ollama locally:** During development/testing. Your RTX 30 series runs `llama3.1:8b` comfortably. Set `PARSER_BACKEND=ollama` in your `.env` for local dev.

---

### 4. TCO Engine (`tco_engine.py`)

Pure Python, no LLM needed. This is deterministic math.

```python
# tco_engine.py
TAX_RATE = 0.0825  # Conroe, TX
PERK_VALUATION_MULTIPLIER = 0.70  # conservative perk valuation

PERK_MSRP = {
    "Galaxy Buds 4": 149.00,
    "Galaxy Buds 4 Pro": 219.00,
    "$30 reserve credit": 30.00,
}

def calculate_tco(deal: dict) -> dict:
    base = deal["base_price"]
    trade_in = deal.get("trade_in_value", 0)
    
    perk_value = sum(
        PERK_MSRP.get(p, 0) * PERK_VALUATION_MULTIPLIER
        for p in deal.get("perks", [])
    )
    
    tax = base * TAX_RATE
    tco = base - trade_in - perk_value + tax
    
    return {**deal, "tco": round(tco, 2), "tax": round(tax, 2), "perk_value": round(perk_value, 2)}
```

---

### 5. Deal Store (`store/`)

**SQLite** for MVP. Zero infrastructure. Runs locally or on your Linux machine.

```sql
CREATE TABLE deals (
    id INTEGER PRIMARY KEY,
    run_date TEXT,
    source TEXT,
    sku TEXT,
    base_price REAL,
    trade_in REAL,
    perk_value REAL,
    tco REAL,
    pickup_available INTEGER,
    urgent INTEGER,
    raw_json TEXT
);
```

**Upgrade path:** Swap SQLite for Supabase (Postgres) when you go multi-device or multi-user. The ORM layer (SQLAlchemy) stays identical.

---

### 6. Notification Layer (`notifier.py`)

**Email:** [Resend](https://resend.com) — generous free tier (3K emails/mo), excellent Python SDK, better DX than SendGrid.

**Push (V1.5):** [ntfy.sh](https://ntfy.sh) — open source, self-hostable, iOS/Android app. Zero cost. One HTTP POST sends a push notification.

```python
# ntfy push for urgent deals
import httpx
httpx.post("https://ntfy.sh/deal-scout-marcus",  # private topic
    data=f"🚨 S26 Ultra TCO at 30-day low: ${tco}. Offer expires Sunday.",
    headers={"Priority": "urgent", "Tags": "money_with_wings"})
```

---

## Development Workflow — Cursor + Claude Code + Gemini

### Recommended Division of Labor

| Task | Best Tool |
|------|-----------|
| Generate scraper boilerplate | Cursor (Cmd+K inline) |
| Debug Playwright async issues | Claude Code (full context) |
| High-volume HTML parsing | Gemini 2.0 Flash API |
| TCO reasoning / email copy | Claude claude-sonnet-4-6 |
| Local testing of parser | Ollama (llama3.1:8b, RTX 30) |
| Cron + infra setup | Claude Code (bash + systemd) |

### Cursor Workflow Tips

1. Open the entire `deal-scout-ai/` project in Cursor.
2. Use **Composer** (not just inline) for multi-file tasks: *"Refactor the TCO engine to support a new `financing_arbitrage` field and update the Deal Store schema accordingly."*
3. Pin `CLAUDE.md` at project root with your config constants (zip, tax rate, perk MSRPs) so Claude Code always has context.
4. Use `.cursorrules` to enforce your coding conventions (typed dataclasses, async-first, no pandas for simple operations).

### Recommended `CLAUDE.md` (drop at project root)

```markdown
# Deal Scout AI — Agent Context

## Owner Config
- Target zip: 77304 (Conroe, TX)
- Tax rate: 8.25%
- Trade-in device: Samsung Galaxy S24 Ultra
- Perk valuation multiplier: 70% of MSRP

## Architecture Principles
- Async-first (asyncio + httpx, not requests)
- AI parser is fallback only — prefer CSS selectors
- All monetary values stored as floats rounded to 2 decimal places
- SQLite for MVP, SQLAlchemy ORM for portability

## API Keys (load from .env, never hardcode)
- ANTHROPIC_API_KEY
- RESEND_API_KEY
- GEMINI_API_KEY (optional, for parser fallback)
```

---

## Project File Structure

```
deal-scout-ai/
├── CLAUDE.md                  ← Agent context for Claude Code
├── .env                       ← API keys (gitignored)
├── config.py                  ← All constants (zip, tax, perks, SKUs)
├── orchestrator.py            ← Main runner
├── scrapers/
│   ├── __init__.py
│   ├── samsung.py             ← Playwright scraper
│   └── bestbuy.py             ← Playwright + store availability API
├── ai_parser.py               ← Claude / Gemini / Ollama fallback
├── tco_engine.py              ← Deterministic TCO calculator
├── store/
│   ├── db.py                  ← SQLAlchemy models + session
│   └── deals.db               ← SQLite file (gitignored)
├── notifier.py                ← Resend email + ntfy.sh push
├── templates/
│   └── digest.html            ← Jinja2 email template
├── tests/
│   ├── test_tco.py
│   └── test_parser.py
├── requirements.txt
└── README.md
```

---

## Cron Setup (Linux — systemd timer, preferred over crontab)

```ini
# /etc/systemd/system/deal-scout.timer
[Unit]
Description=Deal Scout AI — Daily Run

[Timer]
OnCalendar=*-*-* 05:00:00 America/Chicago
Persistent=true

[Install]
WantedBy=timers.target
```

```ini
# /etc/systemd/system/deal-scout.service
[Unit]
Description=Deal Scout AI Runner

[Service]
Type=oneshot
WorkingDirectory=/home/ablo/deal-scout-ai
ExecStart=/home/ablo/deal-scout-ai/.venv/bin/python orchestrator.py
EnvironmentFile=/home/ablo/deal-scout-ai/.env
```

```bash
sudo systemctl enable --now deal-scout.timer
sudo systemctl status deal-scout.timer
```

---

## Phase Roadmap

| Phase | Scope | Timeline | Success Gate |
|-------|-------|----------|--------------|
| **0 — Scaffold** | Project structure, config, SQLite schema | Day 1 | `python orchestrator.py` runs without error |
| **1 — Scrape** | Samsung + Best Buy scrapers for S26 Ultra | Week 1 | Raw deal data extracted and stored |
| **2 — TCO** | TCO engine + ranking | Week 1–2 | TCO within ±5% of manual calc |
| **3 — Notify** | Email digest via Resend | Week 2 | Digest received by 6 AM CT |
| **4 — Harden** | Error handling, cron, 14-day run streak | Week 3 | Zero manual interventions for 14 days |
| **5 — Extend** | Carrier deals, push notifications, trend charts | Month 2 | — |
| **6 — Travel** | Delta flight tracking Epic | Month 3+ | — |

---

## PM Pushback — Scope Risks to Watch

1. **"Let's add Amazon."** Resist. Amazon's Galaxy S26 pricing mirrors Samsung.com but without the trade-in intelligence. Add it in V2 only if it surfaces unique deals in testing.

2. **"Let's build a dashboard."** Not in MVP. The email digest IS the UI. A dashboard adds React, hosting, auth — 3+ weeks of work before you've validated the core value.

3. **"Let's track 5 devices at once."** One device, proven. Then scale the config. The scraper architecture supports multi-SKU from day one — you don't need to build it, just don't expose it yet.

4. **"Let's sell this as a SaaS."** Only after 30 days of personal use with measurable savings. Premature monetization before product-market fit kills more projects than scope creep.

---

*Documentation generated by Deal Scout AI PM Discovery Session — Feb 2026*
*Next step: Claude Code init prompt → scaffold the project structure and generate `config.py` + `tco_engine.py` first (zero external dependencies, fastest to validate).*
