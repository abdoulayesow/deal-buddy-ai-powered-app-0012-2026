"""
Abstract base class for all scrapers.
Every scraper must implement fetch() and return a list of RawDeal.
"""
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone

try:
    from dateutil import parser as dateutil_parser
except ImportError:
    dateutil_parser = None  # type: ignore

# E-05: urgency threshold in seconds (72 hours)
URGENCY_THRESHOLD_SECONDS = 72 * 3600

# Regex patterns for deadline extraction
URGENCY_PATTERNS = [
    r"offer[s]?\s+end[s]?[:\s]+([^\.\n]+)",
    r"expire[s]?\s+(?:on\s+)?([^\.\n]+)",
    r"valid\s+until\s+([^\.\n]+)",
    r"deadline[:\s]+([^\.\n]+)",
]


def _parse_urgency(deadline_str: str) -> tuple[bool, str | None]:
    """
    E-05: Parse deadline string and set urgent=True only when <= 72 hours.
    Returns (urgent, urgency_deadline). If unparseable, returns (True, deadline_str) (conservative).
    """
    if not deadline_str or not deadline_str.strip():
        return False, None
    deadline_str = deadline_str.strip()
    if not dateutil_parser:
        return True, deadline_str  # No dateutil: conservative
    try:
        parsed = dateutil_parser.parse(deadline_str, fuzzy=True)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        delta_seconds = (parsed - now).total_seconds()
        urgent = 0 < delta_seconds <= URGENCY_THRESHOLD_SECONDS
        return urgent, deadline_str
    except (ValueError, TypeError, OverflowError):
        return True, deadline_str  # Unparseable: conservative


def _extract_urgency_deadline(page_text: str) -> tuple[bool, str | None]:
    """Extract urgency deadline from page text. Returns (urgent, urgency_deadline)."""
    if not page_text:
        return False, None
    for pattern in URGENCY_PATTERNS:
        match = re.search(pattern, page_text, re.IGNORECASE)
        if match:
            deadline_str = match.group(1).strip()
            return _parse_urgency(deadline_str)
    return False, None


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

