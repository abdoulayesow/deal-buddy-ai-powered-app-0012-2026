"""
N-04: Purchase log and last-digest persistence.
- last_digest.json: snapshot of best deal from latest digest (for BUY reply matching).
- purchases.json: append-only log of {purchased_at, deal}.
"""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

from tco_engine import ScoredDeal

logger = logging.getLogger(__name__)

# Project root (parent of store/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
LAST_DIGEST_PATH = PROJECT_ROOT / "data" / "last_digest.json"
PURCHASES_PATH = PROJECT_ROOT / "data" / "purchases.json"
_PURCHASES_LOCK = Lock()


def _deal_to_dict(deal: ScoredDeal) -> dict:
    """Convert ScoredDeal to JSON-serializable dict for logging."""
    return {
        "source": deal.source,
        "sku": deal.sku,
        "base_price": deal.base_price,
        "trade_in_value": deal.trade_in_value,
        "perk_value": deal.perk_value,
        "tax": deal.tax,
        "tco": deal.tco,
        "financing_benefit": deal.financing_benefit,
        "source_url": deal.source_url,
        "monthly_payment": deal.monthly_payment,
        "term_months": deal.term_months,
        "lock_in_penalty": deal.lock_in_penalty,
    }


def save_last_digest(best_deal: ScoredDeal) -> None:
    """Persist best deal from digest so BUY reply can match."""
    path = LAST_DIGEST_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"updated_at": datetime.now(timezone.utc).isoformat(), "deal": _deal_to_dict(best_deal)}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    logger.info("Last digest saved to %s", path)


def load_last_digest() -> dict | None:
    """Load last digest snapshot. Returns None if missing or invalid."""
    if not LAST_DIGEST_PATH.exists():
        return None
    try:
        with open(LAST_DIGEST_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Could not load last_digest.json: %s", e)
        return None


def append_purchase(deal: dict) -> None:
    """Append a purchase entry to purchases.json (process-safe within a single worker)."""
    path = PURCHASES_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {"purchased_at": datetime.now(timezone.utc).isoformat(), "deal": deal}

    with _PURCHASES_LOCK:
        existing: list = []
        if path.exists():
            try:
                with open(path, encoding="utf-8") as f:
                    existing = json.load(f)
            except (json.JSONDecodeError, OSError):
                existing = []
        if not isinstance(existing, list):
            existing = []
        existing.append(entry)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2)
    logger.info("Purchase logged: %s @ %s", deal.get("source"), deal.get("tco"))
