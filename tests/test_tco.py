"""
Unit tests for tco_engine.py
"""
import pytest
from scrapers.base import RawDeal
from tco_engine import calculate_tco, rank_deals, ScoredDeal


def test_calculate_tco_no_perks_no_tradein():
    """Test TCO calculation with no perks and no trade-in."""
    deal = RawDeal(
        source="samsung",
        sku="Galaxy S26 Ultra 512GB",
        base_price=1299.99,
        trade_in_value=0.0,
        perks=[],
    )
    scored = calculate_tco(deal)

    # tax = 1299.99 * 0.0825 = 107.25
    # financing_benefit = 1299.99 * (5.5/100) * (24/12) = 143.00
    # TCO = base_price - trade_in - perk_value - financing_benefit + tax = 1264.24
    assert scored.tco == pytest.approx(1264.24, abs=0.01)
    assert scored.base_price == pytest.approx(1299.99, abs=0.01)
    assert scored.trade_in_value == 0.0
    assert scored.perk_value == 0.0
    assert scored.financing_benefit == pytest.approx(143.00, abs=0.01)
    assert scored.tax == pytest.approx(107.25, abs=0.01)


def test_calculate_tco_with_galaxy_buds_4():
    """Test TCO calculation with Galaxy Buds 4 perk."""
    deal = RawDeal(
        source="samsung",
        sku="Galaxy S26 Ultra 512GB",
        base_price=1299.99,
        trade_in_value=0.0,
        perks=["Galaxy Buds 4"],
    )
    scored = calculate_tco(deal)

    # perk_value = 149.00 * 0.70 = 104.30; financing_benefit = 143.00
    # TCO = 1299.99 - 0 - 104.30 - 143.00 + 107.25 = 1159.94
    assert scored.perk_value == pytest.approx(104.30, abs=0.01)
    assert scored.tco == pytest.approx(1159.94, abs=0.01)


def test_calculate_tco_with_reserve_credit():
    """Test TCO calculation with $30 reserve credit perk."""
    deal = RawDeal(
        source="samsung",
        sku="Galaxy S26 Ultra 512GB",
        base_price=1299.99,
        trade_in_value=0.0,
        perks=["$30 reserve credit"],
    )
    scored = calculate_tco(deal)

    # perk_value = 21.00; financing_benefit = 143.00
    # TCO = 1299.99 - 0 - 21.00 - 143.00 + 107.25 = 1243.24
    assert scored.perk_value == pytest.approx(21.00, abs=0.01)
    assert scored.tco == pytest.approx(1243.24, abs=0.01)


def test_calculate_tco_with_double_up_storage():
    """Test TCO calculation with Double up your storage perk (256GB→512GB value $200)."""
    deal = RawDeal(
        source="samsung",
        sku="Galaxy S26 Ultra 512GB",
        base_price=1299.99,
        trade_in_value=0.0,
        perks=["Double up your storage"],
    )
    scored = calculate_tco(deal)

    # perk_value = 140.00; financing_benefit = 143.00
    # TCO = 1299.99 - 0 - 140.00 - 143.00 + 107.25 = 1124.24
    assert scored.perk_value == pytest.approx(140.00, abs=0.01)
    assert scored.tco == pytest.approx(1124.24, abs=0.01)


def test_calculate_tco_with_2x_value():
    """Test TCO calculation with 2x value perk (generic promo)."""
    deal = RawDeal(
        source="samsung",
        sku="Galaxy S26 Ultra 512GB",
        base_price=1299.99,
        trade_in_value=0.0,
        perks=["2x value"],
    )
    scored = calculate_tco(deal)

    # perk_value = 35.00; financing_benefit = 143.00
    # TCO = 1299.99 - 0 - 35.00 - 143.00 + 107.25 = 1229.24
    assert scored.perk_value == pytest.approx(35.00, abs=0.01)
    assert scored.tco == pytest.approx(1229.24, abs=0.01)


def test_calculate_tco_with_unknown_perk():
    """Test TCO calculation with unknown perk (should value at $0)."""
    deal = RawDeal(
        source="samsung",
        sku="Galaxy S26 Ultra 512GB",
        base_price=1299.99,
        trade_in_value=0.0,
        perks=["Unknown Bonus Item"],
    )
    scored = calculate_tco(deal)

    # Unknown perk should be valued at $0
    assert scored.perk_value == 0.0
    # TCO same as no perks (with financing benefit)
    assert scored.tco == pytest.approx(1264.24, abs=0.01)


def test_calculate_tco_financing_benefit():
    """C-03: Financing arbitrage reduces TCO for 0% APR deals."""
    deal = RawDeal(
        source="samsung",
        sku="Galaxy S26 Ultra 512GB",
        base_price=1000.00,
        trade_in_value=0.0,
        perks=[],
    )
    scored = calculate_tco(deal)
    # financing_benefit = 1000 * (5.5/100) * (24/12) = 110.00
    assert scored.financing_benefit == pytest.approx(110.00, abs=0.01)
    # tax = 82.50; TCO = 1000 - 0 - 0 - 110 + 82.50 = 972.50
    assert scored.tco == pytest.approx(972.50, abs=0.01)


def test_rank_deals_sorts_by_tco():
    """Test that rank_deals sorts by TCO ascending."""
    deals = [
        ScoredDeal(
            source="bestbuy",
            sku="Galaxy S26 Ultra 512GB",
            base_price=1349.99,
            trade_in_value=0.0,
            perk_value=0.0,
            tax=111.37,
            tco=1318.36,
            financing_benefit=148.50,
            pickup_available=False,
            urgent=False,
            urgency_deadline=None,
            source_url="",
        ),
        ScoredDeal(
            source="samsung",
            sku="Galaxy S26 Ultra 512GB",
            base_price=1299.99,
            trade_in_value=0.0,
            perk_value=104.30,
            tax=107.25,
            tco=1159.94,
            financing_benefit=143.00,
            pickup_available=False,
            urgent=False,
            urgency_deadline=None,
            source_url="",
        ),
    ]

    ranked = rank_deals(deals)

    assert len(ranked) == 2
    assert ranked[0].source == "samsung"  # Lower TCO
    assert ranked[0].tco == pytest.approx(1159.94, abs=0.01)
    assert ranked[1].source == "bestbuy"
    assert ranked[1].tco == pytest.approx(1318.36, abs=0.01)


def test_realistic_samsung_vs_bestbuy_scenario():
    """Test realistic scenario: Samsung wins on TCO due to perks."""
    samsung_deal = RawDeal(
        source="samsung",
        sku="Galaxy S26 Ultra 512GB",
        base_price=1299.99,
        trade_in_value=500.00,
        perks=["Galaxy Buds 4", "$50 reserve credit"],
        pickup_available=True,
    )
    
    bestbuy_deal = RawDeal(
        source="bestbuy",
        sku="Galaxy S26 Ultra 512GB",
        base_price=1249.99,
        trade_in_value=450.00,
        perks=[],
        pickup_available=True,
    )
    
    samsung_scored = calculate_tco(samsung_deal)
    bestbuy_scored = calculate_tco(bestbuy_deal)

    # Samsung: perk_value = 139.30; financing_benefit = 143.00
    # TCO = 1299.99 - 500 - 139.30 - 143 + 107.25 = 624.94
    assert samsung_scored.perk_value == pytest.approx(139.30, abs=0.01)
    assert samsung_scored.tco == pytest.approx(624.94, abs=0.01)

    # Best Buy: financing_benefit = 1249.99 * 0.11 = 137.50
    # TCO = 1249.99 - 450 - 0 - 137.50 + 103.12 = 765.61
    assert bestbuy_scored.tco == pytest.approx(765.61, abs=0.01)
    
    # Samsung should win (lower TCO)
    ranked = rank_deals([samsung_scored, bestbuy_scored])
    assert ranked[0].source == "samsung"
    assert ranked[0].tco < ranked[1].tco

