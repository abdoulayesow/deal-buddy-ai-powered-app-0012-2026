"""
Abstract base class for all scrapers.
Every scraper must implement fetch() and return a list of RawDeal.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


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

