"""
TCO Engine — pure math. No I/O. No LLM. No side effects.
All monetary inputs and outputs in USD float.
"""
from dataclasses import dataclass
from config import SALES_TAX_RATE, PERK_MSRP, PERK_VALUATION_MULTIPLIER
from scrapers.base import RawDeal


@dataclass
class ScoredDeal:
    source: str
    sku: str
    base_price: float
    trade_in_value: float
    perk_value: float
    tax: float
    tco: float
    pickup_available: bool
    urgent: bool
    urgency_deadline: str | None
    source_url: str
    is_30d_low: bool = False     # set by orchestrator after DB comparison


def calculate_tco(deal: RawDeal) -> ScoredDeal:
    """
    TCO = base_price - trade_in - perk_value + tax

    perk_value = sum of MSRP for each recognized perk × PERK_VALUATION_MULTIPLIER
    Unrecognized perks are logged but valued at $0 to avoid inflation.
    """
    perk_value = sum(
        PERK_MSRP.get(perk, 0.0) * PERK_VALUATION_MULTIPLIER
        for perk in deal.perks
    )
    tax = round(deal.base_price * SALES_TAX_RATE, 2)
    tco = round(deal.base_price - deal.trade_in_value - perk_value + tax, 2)

    return ScoredDeal(
        source=deal.source,
        sku=deal.sku,
        base_price=round(deal.base_price, 2),
        trade_in_value=round(deal.trade_in_value, 2),
        perk_value=round(perk_value, 2),
        tax=tax,
        tco=tco,
        pickup_available=deal.pickup_available,
        urgent=deal.urgent,
        urgency_deadline=deal.urgency_deadline,
        source_url=deal.source_url,
    )


def rank_deals(deals: list[ScoredDeal]) -> list[ScoredDeal]:
    """Sort by TCO ascending. Lowest cost first."""
    return sorted(deals, key=lambda d: d.tco)

