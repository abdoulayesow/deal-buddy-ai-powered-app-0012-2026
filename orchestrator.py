"""
Main entry point. Called by cron at 05:00 CT daily.
Never raises — all errors are caught and logged.
"""
import asyncio
import logging
from datetime import datetime, timezone, timedelta

from config import TRACKED_SKUS, TARGET_ZIP, THIRTY_DAY_WINDOW_DAYS, CARRIER_SCRAPERS_ENABLED
from scrapers.samsung import SamsungScraper
from scrapers.bestbuy import BestBuyScraper
from scrapers.carrier import ATTScraper, TMobileScraper, VerizonScraper
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
if CARRIER_SCRAPERS_ENABLED:
    SCRAPERS.extend([ATTScraper(), TMobileScraper(), VerizonScraper()])


async def run() -> None:
    init_db()
    session = get_session()
    run_log = RunLog(run_date=datetime.now(timezone.utc), status="partial")
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

    # Mark 30-day low (N-02: compare to last 30 days only)
    best_tco = ranked[0].tco
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=THIRTY_DAY_WINDOW_DAYS)
    thirty_day_min = session.query(Deal).filter(
        Deal.sku == ranked[0].sku,
        Deal.run_date >= thirty_days_ago,
    ).order_by(Deal.tco.asc()).first()
    if thirty_day_min is None or best_tco < thirty_day_min.tco:
        ranked[0].is_30d_low = True

    # Persist to DB
    for deal in ranked:
        session.add(Deal(
            source=deal.source, sku=deal.sku,
            base_price=deal.base_price, trade_in_value=deal.trade_in_value,
            perk_value=deal.perk_value, tax=deal.tax, tco=deal.tco,
            financing_benefit=deal.financing_benefit,
            pickup_available=deal.pickup_available,
            urgent=deal.urgent, urgency_deadline=deal.urgency_deadline,
            source_url=deal.source_url,
            monthly_payment=deal.monthly_payment,
            term_months=deal.term_months,
            lock_in_penalty=deal.lock_in_penalty,
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

