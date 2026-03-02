"""
Central configuration. All constants and env vars loaded here.
No other file should call os.environ or dotenv directly.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- Owner ---
TARGET_ZIP = "77304"
THIRTY_DAY_WINDOW_DAYS = 30  # N-02: 30-day low comparison window
SALES_TAX_RATE = 0.0825
# C-03: Financing arbitrage (Revolut 5.5% APY). Benefit = principal × apy × term.
SAVINGS_APY = float(os.getenv("SAVINGS_APY", "5.5"))
FINANCING_TERM_MONTHS_DEFAULT = 24  # Assume 24mo 0% for lump-sum deals
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
    "Double up your storage": 200.00,  # S26 Ultra 256GB→512GB upgrade value
    "2x value": 50.00,  # generic promo; conservative estimate
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
# Fallback when unset or empty (e.g. RESEND_FROM_EMAIL= in .env)
RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL") or "Deal Scout AI <onboarding@resend.dev>"

# --- Best Buy ---
# Conroe, TX Best Buy store ID — verify at bestbuy.com/site/store-locator
BESTBUY_CONROE_STORE_ID = "1565"

# Best Buy SKU mapping: product name -> SKU ID (numeric)
# Empty string = discover from search. Use S25 Ultra (6612728) for testing until S26 listed.
BESTBUY_SKU_MAP: dict[str, str] = {
    "Samsung Galaxy S26 Ultra 512GB": "6612728",  # S25 Ultra 512GB for testing; update when S26 listed
}

# E-03: Carrier device page URLs (SKU -> carrier -> URL). Empty = skip that carrier.
CARRIER_URLS: dict[str, dict[str, str]] = {
    "Samsung Galaxy S26 Ultra 512GB": {
        "att": "https://www.att.com/smartphones/samsung-galaxy-s25-ultra/",
        "tmobile": "https://www.t-mobile.com/cell-phone/samsung-galaxy-s25-ultra",
        "verizon": "https://www.verizon.com/smartphones/samsung-galaxy-s25-ultra/",
    },
}
CARRIER_SCRAPERS_ENABLED = os.getenv("CARRIER_SCRAPERS_ENABLED", "false").lower() == "true"
