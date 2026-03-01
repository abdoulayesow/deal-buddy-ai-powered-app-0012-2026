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

