"""
Best Buy scraper using Playwright and priceBlocks API.
CSS-first extraction with AI parser fallback.
Uses BESTBUY_SKU_MAP from config; discovers SKU from search when not mapped.
"""
import logging
import re
import httpx
from playwright.async_api import async_playwright, Page

from config import BESTBUY_CONROE_STORE_ID, BESTBUY_SKU_MAP
from scrapers.base import BaseScraper, RawDeal, _extract_urgency_deadline

logger = logging.getLogger(__name__)

PAGE_LOAD_TIMEOUT_MS = 30000
API_TIMEOUT_S = 10.0
PRICE_MIN, PRICE_MAX = 500, 2500
TRADE_IN_MIN, TRADE_IN_MAX = 100, 1000


def _parse_pickup_from_api(data: dict) -> bool:
    """Parse pickup availability from priceBlocks API response. Structure may vary."""
    s = str(data).lower()
    if "unavailable" in s and "pickup" in s:
        return False
    if "pickup" in s and ("available" in s or "ready" in s or "today" in s):
        return True
    # Nested structure: common Best Buy API patterns
    for key in ("fulfillment", "pickup", "availability", "stores"):
        if key in data:
            val = data[key]
            if isinstance(val, dict):
                if _parse_pickup_from_api(val):
                    return True
            elif isinstance(val, str) and "available" in val.lower():
                return True
            elif isinstance(val, list):
                for item in val:
                    if isinstance(item, dict) and _parse_pickup_from_api(item):
                        return True
    return False


class BestBuyScraper(BaseScraper):
    source_name = "bestbuy"

    def _get_sku_id(self, sku: str) -> str | None:
        """Get Best Buy SKU ID from config. Empty string = use discovery."""
        mapped = BESTBUY_SKU_MAP.get(sku, "").strip()
        return mapped if mapped else None

    async def _discover_sku_from_search(self, page: Page, sku: str) -> str | None:
        """Search Best Buy, click first result, extract skuId from URL."""
        search_url = f"https://www.bestbuy.com/site/searchpage.jsp?st={sku.replace(' ', '+')}"
        await page.goto(search_url, wait_until="networkidle", timeout=PAGE_LOAD_TIMEOUT_MS)
        product_link = page.locator('a[href*="/site/"][href*=".p?"], a[href*="skuId="]').first
        if await product_link.count() == 0:
            return None
        await product_link.click()
        await page.wait_for_load_state("networkidle")
        url = page.url
        match = re.search(r"skuId=(\d+)", url, re.IGNORECASE)
        if match:
            return match.group(1)
        match = re.search(r"/site/[^/]+/(\d+)\.p", url)
        if match:
            return match.group(1)
        return None

    async def fetch(self, sku: str, zip_code: str) -> list[RawDeal]:
        """
        Fetch deal data from Best Buy for the given SKU.
        Uses config SKU map or discovers from search. Validates pickup via priceBlocks API
        for Conroe store (zip 77304). zip_code param reserved for future store lookup.
        Returns empty list on failure.
        """
        try:
            bb_sku_id = self._get_sku_id(sku)

            async with async_playwright() as p:
                logger.info(f"Starting Best Buy scraper for SKU: {sku}")
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                if bb_sku_id:
                    # Direct product URL when SKU known
                    product_url = f"https://www.bestbuy.com/site/{bb_sku_id}.p?skuId={bb_sku_id}"
                    logger.info(f"Navigating to product URL (skuId={bb_sku_id})")
                    await page.goto(product_url, wait_until="networkidle", timeout=PAGE_LOAD_TIMEOUT_MS)
                else:
                    # Discover SKU from search
                    bb_sku_id = await self._discover_sku_from_search(page, sku)
                    if not bb_sku_id:
                        logger.warning("Could not discover Best Buy SKU from search")
                        await browser.close()
                        return []

                source_url = page.url
                raw_html = await page.content()
                page_text = await page.text_content() or ""

                parse_method = "css"
                base_price = 0.0
                trade_in_value = 0.0
                perks: list[str] = []
                pickup_available = False

                try:
                    price_selectors = [
                        '[data-testid*="price"]',
                        '.priceView-customer-price',
                        '.pricing-price__value',
                        'span[class*="price"]',
                        '[data-automation-id="customer-price"]',
                    ]
                    for selector in price_selectors:
                        price_elem = page.locator(selector).first
                        if await price_elem.count() > 0:
                            price_text = await price_elem.text_content()
                            if price_text:
                                match = re.search(r"\$?([\d,]+\.?\d*)", price_text.replace(",", ""))
                                if match:
                                    val = float(match.group(1))
                                    if PRICE_MIN < val < PRICE_MAX:
                                        base_price = val
                                        logger.info(f"Extracted base_price: ${base_price}")
                                        break
                        if base_price > 0:
                            break

                    if base_price == 0.0:
                        match = re.search(r"\$([\d,]+\.?\d*)", page_text)
                        if match:
                            val = float(match.group(1).replace(",", ""))
                            if PRICE_MIN < val < PRICE_MAX:
                                base_price = val
                                logger.info(f"Extracted base_price from text: ${base_price}")

                    if base_price == 0.0:
                        raise ValueError("Could not extract base_price")

                    trade_in_selectors = [
                        '[data-testid*="trade"]',
                        '[class*="trade"]',
                        'text=/trade.*in/i',
                        r'text=/up to \$/i',
                    ]
                    for selector in trade_in_selectors:
                        trade_elem = page.locator(selector).first
                        if await trade_elem.count() > 0:
                            trade_text = await trade_elem.text_content()
                            if trade_text:
                                match = re.search(r"\$?([\d,]+)", trade_text.replace(",", ""))
                                if match:
                                    trade_in_value = float(match.group(1))
                                    if TRADE_IN_MIN < trade_in_value < TRADE_IN_MAX:
                                        logger.info(f"Extracted trade_in_value: ${trade_in_value}")
                                        break
                        if trade_in_value > 0:
                            break

                    perk_selectors = [
                        '[data-testid*="perk"]',
                        '[class*="bonus"]',
                        '[class*="credit"]',
                    ]
                    for selector in perk_selectors:
                        loc = page.locator(selector)
                        for i in range(await loc.count()):
                            t = await loc.nth(i).text_content()
                            if t and t.strip():
                                perks.append(t.strip())
                    perks = list(dict.fromkeys(perks))
                    logger.info(f"Extracted {len(perks)} perks")

                except Exception as e:
                    logger.warning(f"CSS extraction failed: {e}. Falling back to AI parser.")
                    parse_method = "ai"

                # priceBlocks API for pickup (77304 / Conroe store)
                try:
                    async with httpx.AsyncClient(
                        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                    ) as client:
                        api_url = f"https://www.bestbuy.com/api/3.0/priceBlocks?skuId={bb_sku_id}&storeId={BESTBUY_CONROE_STORE_ID}"
                        response = await client.get(api_url, timeout=API_TIMEOUT_S)
                        if response.status_code == 200:
                            data = response.json()
                            pickup_available = _parse_pickup_from_api(data)
                            if pickup_available:
                                logger.info("Pickup available via priceBlocks API")
                except Exception as e:
                    logger.warning(f"Best Buy priceBlocks API failed: {e}")

                if not pickup_available:
                    pickup_loc = page.locator('text=/pick up today/i, text=/pickup available/i, text=/available for pickup/i')
                    if await pickup_loc.count() > 0:
                        pickup_available = True
                        logger.info("Pickup available detected on page")

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

                logger.info(f"Best Buy scraper completed. Parse method: {parse_method}")
                return [deal]

        except Exception as e:
            logger.error(f"Best Buy scraper failed for {sku}: {e}")
            return []
