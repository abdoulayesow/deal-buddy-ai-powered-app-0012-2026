# COMPOSER INIT — Deal Scout AI
> Paste this entire file into Cursor Composer (Cmd+Shift+I). Do not modify before first run.
> Goal: Scaffold Phase 0 + Phase 1 of Deal Scout AI. Working scraper → TCO → email digest.

---

## YOUR TASK

You are initializing a Python project called `deal-scout-ai`. Execute every step below in order. Create all files. Do not skip any file. Do not ask clarifying questions — use the specs provided.

---

## STEP 1 — Project Bootstrap

Create the following directory structure exactly:

```
deal-scout-ai/
├── CLAUDE.md
├── .env.example
├── .gitignore
├── requirements.txt
├── config.py
├── orchestrator.py
├── scrapers/
│   ├── __init__.py
│   ├── base.py
│   ├── samsung.py
│   └── bestbuy.py
├── ai_parser.py
├── tco_engine.py
├── store/
│   ├── __init__.py
│   ├── db.py
│   └── models.py
├── notifier.py
├── templates/
│   └── digest.html
└── tests/
    ├── __init__.py
    ├── test_tco.py
    └── test_parser.py
```

---

## STEP 2 — File Specifications

### `.gitignore`
```
.env
*.db
__pycache__/
.venv/
*.pyc
.playwright/
```

---

### `.env.example`
```
ANTHROPIC_API_KEY=your_key_here
RESEND_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
NOTIFY_EMAIL=your_email@gmail.com
NTFY_TOPIC=deal-scout-private-topic
PARSER_BACKEND=claude        # options: claude | gemini | ollama
OLLAMA_MODEL=llama3.1:8b
OLLAMA_BASE_URL=http://localhost:11434
```

---

### `requirements.txt`
Pin these exact versions:
```
python-dotenv==1.0.1
playwright==1.44.0
httpx==0.27.0
anthropic==0.28.0
google-generativeai==0.7.2
sqlalchemy==2.0.30
jinja2==3.1.4
resend==2.1.0
pytest==8.2.2
pytest-asyncio==0.23.7
```

---

### `CLAUDE.md`
```markdown
# Deal Scout AI — Agent Context

## Owner Config
- Target zip: 77304 (Conroe, TX)
- Sales tax rate: 8.25%
- Trade-in device: Samsung Galaxy S24 Ultra
- Perk valuation multiplier: 0.70 (70% of MSRP)
- Digest delivery target: 06:00 CT daily

## Active SKUs (Phase 1)
- Samsung Galaxy S26 Ultra 512GB (all colors)

## Architecture Rules
1. Async-first. Use asyncio + httpx. Never use requests.
2. CSS selectors are primary extraction method. AI parser is fallback ONLY.
3. AI parser fallback chain: claude → gemini → ollama (in that order).
4. All monetary values: Python float, round to 2 decimal places.
5. Never hardcode API keys. Always load from .env via config.py.
6. SQLAlchemy ORM only. No raw SQL strings.
7. Type every function signature. Use dataclasses for data objects.

## Key Files
- config.py        → all constants and env loading
- tco_engine.py    → pure math, no I/O, no LLM
- orchestrator.py  → main entry point
- ai_parser.py     → LLM fallback, handles all three backends
```

---

### `config.py`

```python
"""
Central configuration. All constants and env vars loaded here.
No other file should call os.environ or dotenv directly.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- Owner ---
TARGET_ZIP = "77304"
SALES_TAX_RATE = 0.0825
TRADE_IN_DEVICE = "Samsung Galaxy S24 Ultra"
PERK_VALUATION_MULTIPLIER = 0.70

# --- SKUs to track ---
TRACKED_SKUS = [
    "Samsung Galaxy S26 Ultra 512GB",
]

# --- Perk MSRP lookup (USD) ---
PERK_MSRP: dict[str, float] = {
    "Galaxy Buds 4": 149.00,
    "Galaxy Buds 4 Pro": 219.00,
    "$30 reserve credit": 30.00,
    "$50 reserve credit": 50.00,
}

# --- AI Parser ---
PARSER_BACKEND = os.getenv("PARSER_BACKEND", "claude")  # claude | gemini | ollama
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# --- API Keys ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# --- Notifications ---
NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL", "")
NTFY_TOPIC = os.getenv("NTFY_TOPIC", "")

# --- Best Buy ---
# Conroe, TX Best Buy store ID — verify at bestbuy.com/site/store-locator
BESTBUY_CONROE_STORE_ID = "1565"
```

---

### `store/models.py`

```python
"""
SQLAlchemy ORM models. Schema is source of truth.
"""
from datetime import datetime
from sqlalchemy import String, Float, Boolean, DateTime, Text, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    source: Mapped[str] = mapped_column(String(64))          # "samsung" | "bestbuy" | "att"
    sku: Mapped[str] = mapped_column(String(128))
    base_price: Mapped[float] = mapped_column(Float)
    trade_in_value: Mapped[float] = mapped_column(Float, default=0.0)
    perk_value: Mapped[float] = mapped_column(Float, default=0.0)
    tax: Mapped[float] = mapped_column(Float, default=0.0)
    tco: Mapped[float] = mapped_column(Float)
    pickup_available: Mapped[bool] = mapped_column(Boolean, default=False)
    urgent: Mapped[bool] = mapped_column(Boolean, default=False)
    urgency_deadline: Mapped[str | None] = mapped_column(String(64), nullable=True)
    perks_raw: Mapped[str] = mapped_column(Text, default="")   # comma-separated
    source_url: Mapped[str] = mapped_column(Text, default="")
    raw_json: Mapped[str] = mapped_column(Text, default="")


class RunLog(Base):
    __tablename__ = "run_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String(16))    # "success" | "partial" | "failed"
    sources_attempted: Mapped[int] = mapped_column(Integer, default=0)
    sources_succeeded: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
```

---

### `store/db.py`

```python
"""
Database session factory and init.
"""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from store.models import Base

DB_PATH = Path(__file__).parent / "deals.db"
ENGINE = create_engine(f"sqlite:///{DB_PATH}", echo=False)


def init_db() -> None:
    """Create all tables if they don't exist."""
    Base.metadata.create_all(ENGINE)


def get_session() -> Session:
    SessionLocal = sessionmaker(bind=ENGINE)
    return SessionLocal()
```

---

### `scrapers/base.py`

```python
"""
Abstract base class for all scrapers.
Every scraper must implement fetch() and return a list of RawDeal.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class RawDeal:
    source: str
    sku: str
    base_price: float
    trade_in_value: float = 0.0
    perks: list[str] = field(default_factory=list)
    pickup_available: bool = False
    urgent: bool = False
    urgency_deadline: str | None = None
    source_url: str = ""
    raw_html: str = ""          # stored for AI parser fallback
    parse_method: str = "css"   # "css" | "ai"


class BaseScraper(ABC):
    source_name: str = ""

    @abstractmethod
    async def fetch(self, sku: str, zip_code: str) -> list[RawDeal]:
        """
        Fetch deal data for a given SKU and zip code.
        Must not raise — return empty list on failure and log the error.
        """
        ...
```

---

### `scrapers/samsung.py`

Implement the Samsung.com scraper using Playwright. Follow these exact rules:

1. Use `async_playwright` context manager.
2. Navigate to `https://www.samsung.com/us/smartphones/galaxy-s/`.
3. Search for the SKU passed in (e.g. "Galaxy S26 Ultra 512GB").
4. Use CSS selectors to extract: `base_price`, `trade_in_value`, `perks` list.
5. If ANY CSS selector fails (element not found), set `raw_html` to page content and set `parse_method = "ai"`. Do NOT raise.
6. Detect urgency: if page contains text matching `r"offer[s]?\s+end[s]?"` (case-insensitive), set `urgent=True` and extract the deadline string.
7. Check pickup at zip 77304: look for "Available for pickup" text near a zip field. Set `pickup_available` accordingly.
8. Return a single-item `list[RawDeal]`. Return `[]` on catastrophic failure.
9. Add structured logging (`import logging`) at INFO level for each extraction step.

---

### `scrapers/bestbuy.py`

Implement the Best Buy scraper. Follow these exact rules:

1. Use `async_playwright` for page content.
2. Additionally, call the Best Buy store availability API to confirm pickup at store ID from `config.BESTBUY_CONROE_STORE_ID`:
   ```
   GET https://www.bestbuy.com/api/3.0/priceBlocks?skuId={BB_SKU_ID}&storeId={STORE_ID}
   ```
   Use `httpx.AsyncClient` for this API call (not Playwright).
3. Same CSS-first, AI-fallback pattern as samsung.py.
4. Same urgency detection regex.
5. Return `list[RawDeal]`. Return `[]` on catastrophic failure.

> NOTE: Best Buy SKU IDs for Galaxy S devices follow the format `SKU_XXXXXXX`. Leave a `TODO` comment with placeholder SKU — it will be filled in when S26 Ultra is listed.

---

### `ai_parser.py`

```python
"""
AI-based HTML parser. Fallback only — called when CSS selectors fail.
Backend priority: claude → gemini → ollama
"""
import json
import logging
import os
import httpx
import anthropic
from config import (
    PARSER_BACKEND, ANTHROPIC_API_KEY,
    GEMINI_API_KEY, OLLAMA_BASE_URL, OLLAMA_MODEL
)

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a precise data extraction agent for e-commerce HTML.
Return ONLY valid JSON. No explanation. No markdown fences. No extra fields."""

USER_PROMPT_TEMPLATE = """
Extract from this HTML snippet:
- base_price (float, USD, required)
- trade_in_value (float, USD, 0.0 if not found)
- perks (list of strings, [] if none)
- pickup_available (bool)
- urgent (bool, true if offer has an expiry deadline)
- urgency_deadline (string or null)

HTML (first 12000 chars):
{html}
"""


async def parse_with_claude(html: str) -> dict:
    client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": USER_PROMPT_TEMPLATE.format(html=html[:12000])}]
    )
    return json.loads(response.content[0].text)


async def parse_with_gemini(html: str) -> dict:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    prompt = SYSTEM_PROMPT + "\n\n" + USER_PROMPT_TEMPLATE.format(html=html[:12000])
    response = await model.generate_content_async(prompt)
    text = response.text.strip().lstrip("```json").rstrip("```").strip()
    return json.loads(text)


async def parse_with_ollama(html: str) -> dict:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": SYSTEM_PROMPT + "\n\n" + USER_PROMPT_TEMPLATE.format(html=html[:8000]),
                "stream": False,
            }
        )
        result = response.json()
        text = result["response"].strip().lstrip("```json").rstrip("```").strip()
        return json.loads(text)


async def parse_deal(html: str) -> dict | None:
    """
    Try each backend in priority order.
    Returns parsed dict or None if all backends fail.
    """
    backends = {
        "claude": parse_with_claude,
        "gemini": parse_with_gemini,
        "ollama": parse_with_ollama,
    }

    # Always start with configured backend, then fall through
    order = [PARSER_BACKEND] + [k for k in backends if k != PARSER_BACKEND]

    for backend_name in order:
        try:
            logger.info(f"AI parser attempting backend: {backend_name}")
            result = await backends[backend_name](html)
            logger.info(f"AI parser succeeded with backend: {backend_name}")
            return result
        except Exception as e:
            logger.warning(f"AI parser backend {backend_name} failed: {e}")
            continue

    logger.error("All AI parser backends failed.")
    return None
```

---

### `tco_engine.py`

```python
"""
TCO Engine — pure math. No I/O. No LLM. No side effects.
All monetary inputs and outputs in USD float.
"""
from dataclasses import dataclass
from config import SALES_TAX_RATE, PERK_MSRP, PERK_VALUATION_MULTIPLIER
from scrapers.base import RawDeal


@dataclass
class ScoredDeal:
    source: str
    sku: str
    base_price: float
    trade_in_value: float
    perk_value: float
    tax: float
    tco: float
    pickup_available: bool
    urgent: bool
    urgency_deadline: str | None
    source_url: str
    is_30d_low: bool = False     # set by orchestrator after DB comparison


def calculate_tco(deal: RawDeal) -> ScoredDeal:
    """
    TCO = base_price - trade_in - perk_value + tax

    perk_value = sum of MSRP for each recognized perk × PERK_VALUATION_MULTIPLIER
    Unrecognized perks are logged but valued at $0 to avoid inflation.
    """
    perk_value = sum(
        PERK_MSRP.get(perk, 0.0) * PERK_VALUATION_MULTIPLIER
        for perk in deal.perks
    )
    tax = round(deal.base_price * SALES_TAX_RATE, 2)
    tco = round(deal.base_price - deal.trade_in_value - perk_value + tax, 2)

    return ScoredDeal(
        source=deal.source,
        sku=deal.sku,
        base_price=round(deal.base_price, 2),
        trade_in_value=round(deal.trade_in_value, 2),
        perk_value=round(perk_value, 2),
        tax=tax,
        tco=tco,
        pickup_available=deal.pickup_available,
        urgent=deal.urgent,
        urgency_deadline=deal.urgency_deadline,
        source_url=deal.source_url,
    )


def rank_deals(deals: list[ScoredDeal]) -> list[ScoredDeal]:
    """Sort by TCO ascending. Lowest cost first."""
    return sorted(deals, key=lambda d: d.tco)
```

---

### `notifier.py`

```python
"""
Notification layer.
- send_digest(): email via Resend
- send_push(): push via ntfy.sh (urgent deals only)
"""
import logging
import httpx
import resend
from jinja2 import Environment, FileSystemLoader
from config import RESEND_API_KEY, NOTIFY_EMAIL, NTFY_TOPIC
from tco_engine import ScoredDeal

logger = logging.getLogger(__name__)
resend.api_key = RESEND_API_KEY

jinja_env = Environment(loader=FileSystemLoader("templates"))


async def send_digest(deals: list[ScoredDeal]) -> None:
    if not deals:
        logger.warning("No deals to send. Skipping digest.")
        return

    best = deals[0]
    subject = f"[Deal Scout] {best.sku} — Best TCO today: ${best.tco:.2f}"
    if best.is_30d_low:
        subject = "🔥 " + subject + " — 30-DAY LOW"

    template = jinja_env.get_template("digest.html")
    html_body = template.render(deals=deals, best=best)

    resend.Emails.send({
        "from": "Deal Scout AI <onboarding@resend.dev>",
        "to": [NOTIFY_EMAIL],
        "subject": subject,
        "html": html_body,
    })
    logger.info(f"Digest sent to {NOTIFY_EMAIL}. Best TCO: ${best.tco:.2f}")


async def send_push(deal: ScoredDeal) -> None:
    if not NTFY_TOPIC:
        return
    message = (
        f"🚨 {deal.sku}\n"
        f"TCO: ${deal.tco:.2f} via {deal.source}\n"
        f"Offer expires: {deal.urgency_deadline or 'soon'}"
    )
    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message,
            headers={"Priority": "urgent", "Tags": "money_with_wings"},
        )
    logger.info(f"Push notification sent for urgent deal: {deal.source}")
```

---

### `templates/digest.html`

Create a clean, readable HTML email template using Jinja2. Requirements:
- Dark header bar with text "Deal Scout AI — Daily Digest"
- One card per deal, sorted by TCO (lowest first)
- Each card shows: Source, Base Price, Trade-In, Perks Value, Tax, **TCO (bold)**
- Best deal card has a green left border
- Urgent deals have a red "⚠️ Offer Expires: {deadline}" badge
- If `is_30d_low` is true on best deal, show "🔥 30-Day Low" badge
- Footer: "Conroe, TX 77304 · Tax rate: 8.25% · Perk valuation: 70% MSRP"
- Inline CSS only (email client compatibility)

---

### `orchestrator.py`

```python
"""
Main entry point. Called by cron at 05:00 CT daily.
Never raises — all errors are caught and logged.
"""
import asyncio
import logging
from datetime import datetime, timezone

from config import TRACKED_SKUS, TARGET_ZIP
from scrapers.samsung import SamsungScraper
from scrapers.bestbuy import BestBuyScraper
from ai_parser import parse_deal
from tco_engine import calculate_tco, rank_deals, ScoredDeal
from store.db import init_db, get_session
from store.models import Deal, RunLog
from notifier import send_digest, send_push

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s"
)
logger = logging.getLogger("orchestrator")

SCRAPERS = [SamsungScraper(), BestBuyScraper()]


async def run() -> None:
    init_db()
    session = get_session()
    run_log = RunLog(run_date=datetime.now(timezone.utc), status="running")
    session.add(run_log)
    session.commit()

    all_scored: list[ScoredDeal] = []
    succeeded = 0

    for sku in TRACKED_SKUS:
        for scraper in SCRAPERS:
            run_log.sources_attempted += 1
            try:
                raw_deals = await scraper.fetch(sku=sku, zip_code=TARGET_ZIP)

                for raw in raw_deals:
                    # AI parser fallback if CSS extraction failed
                    if raw.parse_method == "ai" and raw.raw_html:
                        logger.info(f"Invoking AI parser for {scraper.source_name}")
                        parsed = await parse_deal(raw.raw_html)
                        if parsed:
                            raw.base_price = parsed.get("base_price", raw.base_price)
                            raw.trade_in_value = parsed.get("trade_in_value", raw.trade_in_value)
                            raw.perks = parsed.get("perks", raw.perks)
                            raw.pickup_available = parsed.get("pickup_available", raw.pickup_available)
                            raw.urgent = parsed.get("urgent", raw.urgent)
                            raw.urgency_deadline = parsed.get("urgency_deadline", raw.urgency_deadline)

                    scored = calculate_tco(raw)
                    all_scored.append(scored)

                succeeded += 1
                run_log.sources_succeeded += 1

            except Exception as e:
                logger.error(f"Scraper {scraper.source_name} failed for {sku}: {e}")

    if not all_scored:
        run_log.status = "failed"
        run_log.error_message = "No deals extracted from any source."
        session.commit()
        logger.error("Run failed — no deals extracted.")
        return

    ranked = rank_deals(all_scored)

    # Mark 30-day low
    best_tco = ranked[0].tco
    thirty_day_min = session.query(Deal).filter(
        Deal.sku == ranked[0].sku
    ).order_by(Deal.tco.asc()).first()
    if thirty_day_min is None or best_tco < thirty_day_min.tco:
        ranked[0].is_30d_low = True

    # Persist to DB
    for deal in ranked:
        session.add(Deal(
            source=deal.source, sku=deal.sku,
            base_price=deal.base_price, trade_in_value=deal.trade_in_value,
            perk_value=deal.perk_value, tax=deal.tax, tco=deal.tco,
            pickup_available=deal.pickup_available,
            urgent=deal.urgent, urgency_deadline=deal.urgency_deadline,
            source_url=deal.source_url,
        ))

    run_log.status = "success" if succeeded == len(SCRAPERS) * len(TRACKED_SKUS) else "partial"
    session.commit()
    session.close()

    # Notify
    await send_digest(ranked)
    for deal in ranked:
        if deal.urgent:
            await send_push(deal)

    logger.info(f"Run complete. {len(ranked)} deals ranked. Best TCO: ${ranked[0].tco:.2f}")


if __name__ == "__main__":
    asyncio.run(run())
```

---

### `tests/test_tco.py`

Write pytest unit tests for `tco_engine.py`. Cover:
1. `calculate_tco()` with no perks, no trade-in → TCO = base_price + tax
2. `calculate_tco()` with Galaxy Buds 4 perk → TCO reduced by $104.30 (149 × 0.70)
3. `calculate_tco()` with $30 reserve credit perk → TCO reduced by $21.00 (30 × 0.70)
4. `calculate_tco()` with unknown perk → perk_value = 0, no error
5. `rank_deals()` → returns list sorted by TCO ascending
6. Test with realistic Samsung vs Best Buy scenario — Samsung wins on TCO

Use `pytest.approx()` for float comparisons. Do not mock — TCO engine has no I/O.

---

### `tests/test_parser.py`

Write pytest unit tests for `ai_parser.py`. Cover:
1. `parse_with_claude()` mocked — assert it calls Anthropic with correct system prompt
2. `parse_deal()` returns `None` when all backends raise exceptions (mock all three)
3. `parse_deal()` falls through to second backend when first raises
4. JSON cleanup strips markdown fences from Gemini/Ollama responses
5. Assert returned dict always has keys: `base_price`, `trade_in_value`, `perks`, `pickup_available`

Use `pytest-asyncio` and `unittest.mock.AsyncMock`.

---

## STEP 3 — Validation Commands

After creating all files, run these commands and show me the output:

```bash
# 1. Create venv and install deps
cd deal-scout-ai
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Install Playwright browser
playwright install chromium

# 3. Run TCO tests (no API keys needed)
pytest tests/test_tco.py -v

# 4. Smoke test orchestrator import
python -c "from orchestrator import run; print('Import OK')"

# 5. Init DB
python -c "from store.db import init_db; init_db(); print('DB initialized')"
```

All 5 commands must pass before you are done. If any fail, fix the code and re-run.

---

## STEP 4 — What You Will NOT Build Yet

Do not build or scaffold any of the following (future phases):
- Delta flight tracking
- Web dashboard or React frontend
- Multi-user support or auth
- Carrier deal scrapers (AT&T, Verizon, T-Mobile)
- Financing arbitrage calculator
- Email reply parsing ("BUY" command)

If you find yourself reaching for any of these, stop and stay in scope.

---

## SUCCESS CRITERIA

You are done when:
- [ ] All files exist at correct paths
- [ ] `pytest tests/test_tco.py` passes with 6 tests green
- [ ] `python -c "from orchestrator import run"` produces no ImportError
- [ ] `store/deals.db` is created by `init_db()`
- [ ] `.env.example` matches all variables consumed in `config.py`

**Do not report done until all 5 validation commands pass.**
