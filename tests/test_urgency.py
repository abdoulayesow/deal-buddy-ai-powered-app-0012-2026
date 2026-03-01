"""
Unit tests for E-05 urgency detection (scrapers/base.py).
"""
from scrapers.base import _extract_urgency_deadline, _parse_urgency


def test_extract_urgency_offer_ends():
    """Offer ends Sunday -> extracts deadline."""
    urgent, deadline = _extract_urgency_deadline("Offer ends Sunday at midnight")
    assert deadline == "Sunday at midnight"
    # urgent depends on whether Sunday is within 72h


def test_extract_urgency_no_match():
    """No deadline text -> no urgency."""
    urgent, deadline = _extract_urgency_deadline("No special offer. Price is $1299.")
    assert deadline is None
    assert urgent is False


def test_extract_urgency_expires():
    """Expires March 3 -> extracts deadline."""
    urgent, deadline = _extract_urgency_deadline("Expires March 3, 2026")
    assert "March" in (deadline or "")
    assert "3" in (deadline or "")


def test_parse_urgency_empty():
    """Empty string -> not urgent."""
    urgent, dl = _parse_urgency("")
    assert urgent is False
    assert dl is None


def test_parse_urgency_unparseable_conservative():
    """Unparseable deadline -> conservative (urgent=True)."""
    urgent, dl = _parse_urgency("sometime soon")
    assert urgent is True
    assert dl == "sometime soon"
