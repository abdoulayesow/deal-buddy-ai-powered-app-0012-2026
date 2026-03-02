"""
Shared carrier scraper logic (E-03).
Implements AT&T, T-Mobile, and Verizon installment deal scraping.
"""
import logging
import re
from typing import Final

from playwright.async_api import async_playwright, Page

from config import CARRIER_URLS
from scrapers.base import BaseScraper, RawDeal, _extract_urgency_deadline

logger = logging.getLogger(__name__)

PAGE_LOAD_TIMEOUT_MS: Final[int] = 30000
CARRIER_PRICE_MIN: Final[float] = 10.0   # Monthly payment range (USD)
CARRIER_PRICE_MAX: Final[float] = 100.0
CARRIER_TERM_DEFAULT_MONTHS: Final[int] = 36


async def _extract_monthly_payment(page: Page) -> float | None:
    """Best-effort monthly payment extraction from common carrier selectors."""
    selectors = [
        '[data-testid*="monthly"]',
        '[class*="monthly"]',
        '[class*="payment"]',
    ]
    for selector in selectors:
        elems = page.locator(selector)
        count = await elems.count()
        for i in range(min(count, 5)):
            text = await elems.nth(i).text_content()
            if not text:
                continue
            match = re.search(r"\$?([\d,]+\.?\d*)", text.replace(",", ""))
            if not match:
                continue
            val = float(match.group(1))
            if CARRIER_PRICE_MIN < val < CARRIER_PRICE_MAX:
                return val
    return None


def _infer_term_months(page_text: str) -> int:
    """Infer installment term from page text, preferring 36 then 24 months."""
    lowered = page_text.lower()
    if re.search(r"\b36\s*month", lowered):
        return 36
    if re.search(r"\b24\s*month", lowered):
        return 24
    return CARRIER_TERM_DEFAULT_MONTHS


def _extract_trade_in_value(page_text: str) -> float:
    """Look for trade-in amounts in text."""
    match = re.search(r"trade[- ]?in[:\s]*\$?([\d,]+\.?\d*)", page_text, re.IGNORECASE)
    if not match:
        return 0.0
    return float(match.group(1).replace(",", ""))


class CarrierScraper(BaseScraper):
    """Generic carrier scraper; concrete classes configure source_name and URL key."""

    def __init__(self, source_name: str, carrier_key: str) -> None:
        self.source_name = source_name
        self._carrier_key = carrier_key

    async def fetch(self, sku: str, zip_code: str) -> list[RawDeal]:
        """
        Fetch installment deal for SKU from configured carrier.
        Returns empty list on failure.
        """
        url_map = CARRIER_URLS.get(sku) or {}
        url = url_map.get(self._carrier_key, "").strip()
        if not url:
            logger.debug("%s: No URL configured for %s", self.source_name, sku)
            return []

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(url, wait_until="networkidle", timeout=PAGE_LOAD_TIMEOUT_MS)
                source_url = page.url
                raw_html = await page.content()
                page_text = await page.text_content() or ""

                monthly_payment = await _extract_monthly_payment(page)
                term_months = _infer_term_months(page_text)

                effective_price: float | None = None
                if monthly_payment is not None and term_months:
                    effective_price = round(monthly_payment * term_months, 2)

                trade_in_value = _extract_trade_in_value(page_text)
                urgent, urgency_deadline = _extract_urgency_deadline(page_text)
                await browser.close()

                if effective_price is None:
                    logger.warning("%s: Could not extract pricing for %s", self.source_name, sku)
                    return []

                deal = RawDeal(
                    source=self.source_name,
                    sku=sku,
                    base_price=effective_price,
                    trade_in_value=round(trade_in_value, 2),
                    perks=[],
                    pickup_available=False,
                    urgent=urgent,
                    urgency_deadline=urgency_deadline,
                    source_url=source_url,
                    raw_html=raw_html,
                    parse_method="css",
                    monthly_payment=round(monthly_payment, 2) if monthly_payment is not None else None,
                    term_months=term_months,
                    lock_in_penalty=None,
                    effective_price=effective_price,
                )
                logger.info(
                    "%s scraper: %s @ $%.2f/mo x %d",
                    self.source_name,
                    sku,
                    monthly_payment or 0,
                    term_months,
                )
                return [deal]

        except Exception as exc:  # noqa: BLE001 - top-level scraper guard
            logger.error("%s scraper failed for %s: %s", self.source_name, sku, exc)
            return []


class ATTScraper(CarrierScraper):
    def __init__(self) -> None:
        super().__init__(source_name="att", carrier_key="att")


class TMobileScraper(CarrierScraper):
    def __init__(self) -> None:
        super().__init__(source_name="tmobile", carrier_key="tmobile")


class VerizonScraper(CarrierScraper):
    def __init__(self) -> None:
        super().__init__(source_name="verizon", carrier_key="verizon")

