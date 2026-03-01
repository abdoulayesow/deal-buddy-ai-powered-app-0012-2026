"""
Samsung.com scraper using Playwright.
CSS-first extraction with AI parser fallback.
Direct navigation to S26 Ultra buy page; selects 512GB variant.
"""
import logging
import re
from playwright.async_api import async_playwright

from scrapers.base import BaseScraper, RawDeal, _extract_urgency_deadline

logger = logging.getLogger(__name__)

SAMSUNG_S26_ULTRA_BUY_URL = "https://www.samsung.com/us/smartphones/galaxy-s26-ultra/buy/"
PAGE_LOAD_TIMEOUT_MS = 30000
VARIANT_SELECT_DELAY_MS = 1500
PRICE_MIN, PRICE_MAX = 500, 2500  # Sanity range for S26 Ultra


class SamsungScraper(BaseScraper):
    source_name = "samsung"

    async def fetch(self, sku: str, zip_code: str) -> list[RawDeal]:
        """
        Fetch deal data from Samsung.com for the given SKU.
        Navigates directly to S26 Ultra buy page, selects 512GB, extracts price/trade-in/perks.
        Returns empty list on failure.
        """
        try:
            async with async_playwright() as p:
                logger.info(f"Starting Samsung scraper for SKU: {sku}")
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                # Direct navigation to buy page
                logger.info("Navigating to Samsung S26 Ultra buy page")
                await page.goto(SAMSUNG_S26_ULTRA_BUY_URL, wait_until="networkidle", timeout=PAGE_LOAD_TIMEOUT_MS)

                # Select 512GB storage variant
                storage_512 = page.locator('button:has-text("512GB"), [role="button"]:has-text("512GB"), label:has-text("512GB")').first
                if await storage_512.count() > 0:
                    await storage_512.click()
                    await page.wait_for_timeout(VARIANT_SELECT_DELAY_MS)

                source_url = page.url
                raw_html = await page.content()
                page_text = await page.text_content() or ""

                parse_method = "css"
                base_price = 0.0
                trade_in_value = 0.0
                perks: list[str] = []
                # Samsung.com is direct-ship; "Where to buy" links to retailers
                pickup_available = False

                try:
                    # Base price — try multiple selectors
                    price_selectors = [
                        '[data-testid*="price"]',
                        '[class*="price"]',
                        '.price',
                        'span:has-text("$")',
                        '[data-automation-id="product-price"]',
                    ]
                    for selector in price_selectors:
                        price_elems = page.locator(selector)
                        for i in range(await price_elems.count()):
                            text = await price_elems.nth(i).text_content()
                            if text:
                                match = re.search(r'\$?([\d,]+\.?\d*)', text.replace(",", ""))
                                if match:
                                    val = float(match.group(1))
                                    if PRICE_MIN < val < PRICE_MAX:
                                        base_price = val
                                        logger.info(f"Extracted base_price: ${base_price}")
                                        break
                        if base_price > 0:
                            break

                    if base_price == 0.0:
                        # Fallback: "From $1,299.99" in page text
                        match = re.search(r'from\s+\$?([\d,]+\.?\d*)', page_text, re.IGNORECASE)
                        if match:
                            base_price = float(match.group(1).replace(",", ""))
                            logger.info(f"Extracted base_price from text: ${base_price}")

                    if base_price == 0.0:
                        raise ValueError("Could not extract base_price")

                    # Trade-in value — "up to $900", "S24 Ultra" specific
                    trade_in_selectors = [
                        '[data-testid*="trade"]',
                        '[class*="trade"]',
                        'text=/trade.*in/i',
                        'text=/instant trade-in/i',
                        r'text=/up to \$/i',
                    ]
                    for selector in trade_in_selectors:
                        elems = page.locator(selector)
                        for i in range(await elems.count()):
                            text = await elems.nth(i).text_content()
                            if text and ("900" in text or "800" in text or "700" in text):
                                match = re.search(r'\$?([\d,]+)', text.replace(",", ""))
                                if match:
                                    trade_in_value = float(match.group(1))
                                    logger.info(f"Extracted trade_in_value: ${trade_in_value}")
                                    break
                        if trade_in_value > 0:
                            break

                    if trade_in_value == 0.0:
                        match = re.search(r'up to \$([\d,]+)\s*(?:instant)?\s*trade-in', page_text, re.IGNORECASE)
                        if match:
                            trade_in_value = float(match.group(1).replace(",", ""))
                            logger.info(f"Extracted trade_in_value from text: ${trade_in_value}")

                    # Perks — specific keywords first; generic "reserve credit" only if no specific match
                    perk_keywords = [
                        "Double up your storage",
                        "Galaxy Buds 4 Pro",
                        "Galaxy Buds 4",
                        "$50 reserve credit",
                        "$30 reserve credit",
                        "2x value",
                    ]
                    page_lower = page_text.lower()
                    for kw in perk_keywords:
                        if kw.lower() in page_lower:
                            perks.append(kw)
                    # Add generic "reserve credit" only if no specific reserve credit matched
                    if "reserve credit" in page_lower and not any("reserve" in p for p in perks):
                        perks.append("reserve credit")
                    perks = list(dict.fromkeys(perks))

                    logger.info(f"Extracted {len(perks)} perks: {perks}")

                except Exception as e:
                    logger.warning(f"CSS extraction failed: {e}. Falling back to AI parser.")
                    parse_method = "ai"

                # E-05: Time-limited deal detection (72h rule)
                urgent, urgency_deadline = _extract_urgency_deadline(page_text)
                if urgency_deadline:
                    logger.info(f"Urgency: urgent={urgent}, deadline={urgency_deadline}")

                await browser.close()

                deal = RawDeal(
                    source=self.source_name,
                    sku=sku,
                    base_price=round(base_price, 2),
                    trade_in_value=round(trade_in_value, 2),
                    perks=perks,
                    pickup_available=pickup_available,
                    urgent=urgent,
                    urgency_deadline=urgency_deadline,
                    source_url=source_url,
                    raw_html=raw_html if parse_method == "ai" else "",
                    parse_method=parse_method,
                )

                logger.info(f"Samsung scraper completed. Parse method: {parse_method}")
                return [deal]

        except Exception as e:
            logger.error(f"Samsung scraper failed for {sku}: {e}")
            return []
