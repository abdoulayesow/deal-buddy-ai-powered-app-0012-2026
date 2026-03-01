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

