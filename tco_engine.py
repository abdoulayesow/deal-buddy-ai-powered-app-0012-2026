"""
TCO Engine — pure math. No I/O. No LLM. No side effects.
All monetary inputs and outputs in USD float.
"""
from dataclasses import dataclass
from config import (
    SALES_TAX_RATE,
    PERK_MSRP,
    PERK_VALUATION_MULTIPLIER,
    SAVINGS_APY,
    FINANCING_TERM_MONTHS_DEFAULT,
)
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
    financing_benefit: float
    pickup_available: bool
    urgent: bool
    urgency_deadline: str | None
    source_url: str
    is_30d_low: bool = False     # set by orchestrator after DB comparison
    # E-03: Carrier deal display
    monthly_payment: float | None = None
    term_months: int | None = None
    lock_in_penalty: float | None = None


def calculate_tco(deal: RawDeal) -> ScoredDeal:
    """
    TCO = cost_base - trade_in - perk_value - financing_benefit + tax

    For retailers: cost_base = base_price.
    For carrier deals (E-03): cost_base = effective_price or monthly_payment * term_months.
    perk_value = sum of MSRP for each recognized perk × PERK_VALUATION_MULTIPLIER
    financing_benefit = principal × (savings_apy/100) × (term_months/12) for 0% APR
    Unrecognized perks are logged but valued at $0 to avoid inflation.
    """
    perk_value = sum(
        PERK_MSRP.get(perk, 0.0) * PERK_VALUATION_MULTIPLIER
        for perk in deal.perks
    )

    # E-03: Carrier deals use effective_price or monthly_payment * term_months
    cost_base = deal.base_price
    if deal.effective_price is not None:
        cost_base = deal.effective_price
    elif deal.monthly_payment is not None and deal.term_months is not None:
        cost_base = deal.monthly_payment * deal.term_months

    tax = round(cost_base * SALES_TAX_RATE, 2)

    # C-03: Financing arbitrage. Use term_months from carrier deals if set.
    term_months = deal.term_months or FINANCING_TERM_MONTHS_DEFAULT
    principal = cost_base
    financing_benefit = round(
        principal * (SAVINGS_APY / 100) * (term_months / 12), 2
    )

    tco = round(
        cost_base - deal.trade_in_value - perk_value - financing_benefit + tax, 2
    )

    return ScoredDeal(
        source=deal.source,
        sku=deal.sku,
        base_price=round(cost_base, 2),
        trade_in_value=round(deal.trade_in_value, 2),
        perk_value=round(perk_value, 2),
        tax=tax,
        tco=tco,
        financing_benefit=financing_benefit,
        pickup_available=deal.pickup_available,
        urgent=deal.urgent,
        urgency_deadline=deal.urgency_deadline,
        source_url=deal.source_url,
        monthly_payment=deal.monthly_payment,
        term_months=deal.term_months,
        lock_in_penalty=deal.lock_in_penalty,
    )


def rank_deals(deals: list[ScoredDeal]) -> list[ScoredDeal]:
    """Sort by TCO ascending. Lowest cost first."""
    return sorted(deals, key=lambda d: d.tco)

