#!/usr/bin/env python3
"""
R-05: Run history / price trends.
Query Deal table by run_date, output TCO range and trend for tracked SKUs.

Usage (recommended from project root):
    python -m scripts.price_trends --days 30 --format human
"""
import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone, timedelta

from store.db import init_db, get_session
from store.models import Deal


def get_trends(days: int = 30) -> list[dict]:
    """Query deals from last N days, aggregate by SKU."""
    init_db()
    session = get_session()
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    rows = (
        session.query(Deal.sku, Deal.run_date, Deal.tco, Deal.source)
        .filter(Deal.run_date >= cutoff)
        .order_by(Deal.run_date.asc())
        .all()
    )
    session.close()

    # Group by SKU: collect (run_date, tco) per source
    by_sku: dict[str, list[tuple[datetime, float, str]]] = defaultdict(list)
    for sku, run_date, tco, source in rows:
        by_sku[sku].append((run_date, tco, source))

    result = []
    for sku, entries in by_sku.items():
        if not entries:
            continue
        dates = sorted(set(e[0] for e in entries))
        tcos = [e[1] for e in entries]
        tco_min = min(tcos)
        tco_max = max(tcos)
        # Trend: compare first vs last run_date's best TCO
        first_date = min(e[0] for e in entries)
        last_date = max(e[0] for e in entries)
        first_tcos = [e[1] for e in entries if e[0] == first_date]
        last_tcos = [e[1] for e in entries if e[0] == last_date]
        best_first = min(first_tcos)
        best_last = min(last_tcos)
        if best_last < best_first:
            trend = "down"
        elif best_last > best_first:
            trend = "up"
        else:
            trend = "flat"

        result.append({
            "sku": sku,
            "dates": [d.isoformat() for d in dates],
            "tco_min": round(tco_min, 2),
            "tco_max": round(tco_max, 2),
            "trend": trend,
            "run_count": len(entries),
        })
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Deal Scout AI — Price trends")
    parser.add_argument("--days", type=int, default=30, help="Days to look back")
    parser.add_argument("--format", choices=["json", "human"], default="json")
    args = parser.parse_args()

    trends = get_trends(days=args.days)

    if args.format == "json":
        print(json.dumps(trends, indent=2))
    else:
        for t in trends:
            print(f"\n{t['sku']}")
            print(f"  Runs: {t['run_count']} | TCO range: ${t['tco_min']:.2f} — ${t['tco_max']:.2f}")
            print(f"  Trend: {t['trend']}")
            print(f"  Dates: {sorted(t['dates'])[:5]}{'...' if len(t['dates']) > 5 else ''}")


if __name__ == "__main__":
    main()
