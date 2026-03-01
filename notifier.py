"""
Notification layer.
- send_digest(): email via Resend
- send_push(): push via ntfy.sh (urgent deals only)
"""
import logging
from pathlib import Path

import httpx
import resend
from jinja2 import Environment, FileSystemLoader
from config import RESEND_API_KEY, NOTIFY_EMAIL, NTFY_TOPIC
from tco_engine import ScoredDeal

logger = logging.getLogger(__name__)
resend.api_key = RESEND_API_KEY

jinja_env = Environment(loader=FileSystemLoader(Path(__file__).parent / "templates"))


async def send_digest(deals: list[ScoredDeal]) -> None:
    if not deals:
        logger.warning("No deals to send. Skipping digest.")
        return

    best = deals[0]
    subject = f"[Deal Scout] {best.sku} — Best TCO today: ${best.tco:.2f}"
    if best.is_30d_low:
        subject = "🔥 " + subject + " — 30-DAY LOW"

    template = jinja_env.get_template("digest.html")
    html_body = template.render(deals=deals, best=best)

    resend.Emails.send({
        "from": "Deal Scout AI <onboarding@resend.dev>",
        "to": [NOTIFY_EMAIL],
        "subject": subject,
        "html": html_body,
    })
    logger.info(f"Digest sent to {NOTIFY_EMAIL}. Best TCO: ${best.tco:.2f}")


async def send_push(deal: ScoredDeal) -> None:
    if not NTFY_TOPIC:
        return
    message = (
        f"🚨 {deal.sku}\n"
        f"TCO: ${deal.tco:.2f} via {deal.source}\n"
        f"Offer expires: {deal.urgency_deadline or 'soon'}"
    )
    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message,
            headers={"Priority": "urgent", "Tags": "money_with_wings"},
        )
    logger.info(f"Push notification sent for urgent deal: {deal.source}")

