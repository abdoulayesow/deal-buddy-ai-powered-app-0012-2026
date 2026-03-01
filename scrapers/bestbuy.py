"""
Best Buy scraper using Playwright and Best Buy API.
CSS-first extraction with AI parser fallback.
"""
import logging
import re
import httpx
from playwright.async_api import async_playwright
from scrapers.base import BaseScraper, RawDeal
from config import BESTBUY_CONROE_STORE_ID

logger = logging.getLogger(__name__)


class BestBuyScraper(BaseScraper):
    source_name = "bestbuy"
    
    # TODO: Replace with actual Best Buy SKU ID when Galaxy S26 Ultra is listed
    # Best Buy SKU IDs for Galaxy S devices follow format: SKU_XXXXXXX
    BB_SKU_ID = "SKU_PLACEHOLDER"

    async def fetch(self, sku: str, zip_code: str) -> list[RawDeal]:
        """
        Fetch deal data from Best Buy for the given SKU.
        Returns empty list on failure.
        """
        try:
            async with async_playwright() as p:
                logger.info(f"Starting Best Buy scraper for SKU: {sku}")
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Navigate to Best Buy search
                logger.info("Navigating to Best Buy")
                search_url = f"https://www.bestbuy.com/site/searchpage.jsp?st={sku.replace(' ', '+')}"
                await page.goto(search_url, wait_until="networkidle")
                
                # Try to find product link
                product_link = page.locator(f'a:has-text("{sku}"), a[href*="/p/"]').first
                if await product_link.count() > 0:
                    await product_link.click()
                    await page.wait_for_load_state("networkidle")
                
                # Get page content for fallback
                raw_html = await page.content()
                source_url = page.url
                
                # Extract data using CSS selectors
                logger.info("Extracting data with CSS selectors")
                parse_method = "css"
                base_price = 0.0
                trade_in_value = 0.0
                perks: list[str] = []
                pickup_available = False
                urgent = False
                urgency_deadline: str | None = None
                
                try:
                    # Try common Best Buy price selectors
                    price_selectors = [
                        '[data-testid*="price"]',
                        '.priceView-customer-price',
                        '.pricing-price__value',
                        'span[class*="price"]',
                    ]
                    for selector in price_selectors:
                        price_elem = page.locator(selector).first
                        if await price_elem.count() > 0:
                            price_text = await price_elem.text_content()
                            if price_text:
                                price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text.replace(',', ''))
                                if price_match:
                                    base_price = float(price_match.group(1))
                                    logger.info(f"Extracted base_price: ${base_price}")
                                    break
                    
                    if base_price == 0.0:
                        raise ValueError("Could not extract base_price")
                    
                    # Try trade-in value selectors
                    trade_in_selectors = [
                        '[data-testid*="trade"]',
                        '[class*="trade"]',
                        'text=/trade.*in/i',
                    ]
                    for selector in trade_in_selectors:
                        trade_elem = page.locator(selector).first
                        if await trade_elem.count() > 0:
                            trade_text = await trade_elem.text_content()
                            if trade_text:
                                trade_match = re.search(r'\$?([\d,]+\.?\d*)', trade_text.replace(',', ''))
                                if trade_match:
                                    trade_in_value = float(trade_match.group(1))
                                    logger.info(f"Extracted trade_in_value: ${trade_in_value}")
                                    break
                    
                    # Extract perks
                    perk_selectors = [
                        '[data-testid*="perk"]',
                        '[class*="bonus"]',
                        '[class*="credit"]',
                    ]
                    for selector in perk_selectors:
                        perk_elems = page.locator(selector)
                        count = await perk_elems.count()
                        for i in range(count):
                            perk_text = await perk_elems.nth(i).text_content()
                            if perk_text:
                                perks.append(perk_text.strip())
                    
                    logger.info(f"Extracted {len(perks)} perks")
                    
                except Exception as e:
                    logger.warning(f"CSS extraction failed: {e}. Falling back to AI parser.")
                    parse_method = "ai"
                
                # Check pickup availability via Best Buy API
                if self.BB_SKU_ID != "SKU_PLACEHOLDER":
                    try:
                        async with httpx.AsyncClient() as client:
                            api_url = f"https://www.bestbuy.com/api/3.0/priceBlocks?skuId={self.BB_SKU_ID}&storeId={BESTBUY_CONROE_STORE_ID}"
                            response = await client.get(api_url, timeout=10.0)
                            if response.status_code == 200:
                                data = response.json()
                                # Check if pickup is available in response
                                if "pickup" in str(data).lower() or "available" in str(data).lower():
                                    pickup_available = True
                                    logger.info("Pickup available via API")
                    except Exception as e:
                        logger.warning(f"Best Buy API call failed: {e}")
                
                # Also check page for pickup text
                if not pickup_available:
                    pickup_text = await page.locator('text=/available.*pickup/i, text=/pickup.*available/i').first.text_content()
                    if pickup_text:
                        pickup_available = True
                        logger.info("Pickup available detected on page")
                
                # Detect urgency
                page_text = await page.text_content()
                urgency_match = re.search(r'offer[s]?\s+end[s]?[:\s]+([^\.\n]+)', page_text or "", re.IGNORECASE)
                if urgency_match:
                    urgent = True
                    urgency_deadline = urgency_match.group(1).strip()
                    logger.info(f"Urgent deal detected. Deadline: {urgency_deadline}")
                
                await browser.close()
                
                # Create RawDeal
                deal = RawDeal(
                    source=self.source_name,
                    sku=sku,
                    base_price=base_price,
                    trade_in_value=trade_in_value,
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

