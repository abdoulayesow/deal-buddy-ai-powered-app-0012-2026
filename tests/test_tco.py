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
    
    # TCO = base_price - trade_in - perk_value + tax
    # tax = 1299.99 * 0.0825 = 107.25
    # TCO = 1299.99 - 0 - 0 + 107.25 = 1407.24
    assert scored.tco == pytest.approx(1407.24, abs=0.01)
    assert scored.base_price == pytest.approx(1299.99, abs=0.01)
    assert scored.trade_in_value == 0.0
    assert scored.perk_value == 0.0
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
    
    # perk_value = 149.00 * 0.70 = 104.30
    # tax = 1299.99 * 0.0825 = 107.25
    # TCO = 1299.99 - 0 - 104.30 + 107.25 = 1302.94
    assert scored.perk_value == pytest.approx(104.30, abs=0.01)
    assert scored.tco == pytest.approx(1302.94, abs=0.01)


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
    
    # perk_value = 30.00 * 0.70 = 21.00
    # tax = 1299.99 * 0.0825 = 107.25
    # TCO = 1299.99 - 0 - 21.00 + 107.25 = 1386.24
    assert scored.perk_value == pytest.approx(21.00, abs=0.01)
    assert scored.tco == pytest.approx(1386.24, abs=0.01)


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
    # TCO should be same as no perks
    assert scored.tco == pytest.approx(1407.24, abs=0.01)


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
            tco=1461.36,
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
            tco=1302.94,
            pickup_available=False,
            urgent=False,
            urgency_deadline=None,
            source_url="",
        ),
    ]
    
    ranked = rank_deals(deals)
    
    assert len(ranked) == 2
    assert ranked[0].source == "samsung"  # Lower TCO
    assert ranked[0].tco == pytest.approx(1302.94, abs=0.01)
    assert ranked[1].source == "bestbuy"
    assert ranked[1].tco == pytest.approx(1461.36, abs=0.01)


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
    
    # Samsung: perk_value = (149.00 + 50.00) * 0.70 = 139.30
    # tax = 1299.99 * 0.0825 = 107.25
    # TCO = 1299.99 - 500.00 - 139.30 + 107.25 = 767.94
    assert samsung_scored.perk_value == pytest.approx(139.30, abs=0.01)
    assert samsung_scored.tco == pytest.approx(767.94, abs=0.01)
    
    # Best Buy: tax = 1249.99 * 0.0825 = 103.12
    # TCO = 1249.99 - 450.00 - 0 + 103.12 = 903.11
    assert bestbuy_scored.tco == pytest.approx(903.11, abs=0.01)
    
    # Samsung should win (lower TCO)
    ranked = rank_deals([samsung_scored, bestbuy_scored])
    assert ranked[0].source == "samsung"
    assert ranked[0].tco < ranked[1].tco

