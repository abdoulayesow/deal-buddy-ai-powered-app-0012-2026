"""
N-04: Resend Inbound webhook server.
POST /webhook/resend receives email.received events; fetches body, looks for "BUY",
matches to last digest deal, appends to data/purchases.json.

Setup:
  1. Resend Dashboard: add a receiving domain (or use .resend.app).
  2. Create Inbound route; set webhook URL to https://your-server.com/webhook/resend.
  3. Ensure RESEND_API_KEY is set (used to fetch email content via Receiving API).

Run: uvicorn webhook_server:app --host 0.0.0.0 --port 8000
"""
import json
import logging
import re

import httpx
from fastapi import BackgroundTasks, FastAPI, Request, Response

from config import RESEND_API_KEY
from store.purchase_log import append_purchase, load_last_digest

logger = logging.getLogger(__name__)


def _fetch_received_email(email_id: str) -> dict | None:
    """GET Resend Receiving API for email body. Returns None on failure."""
    if not RESEND_API_KEY or not RESEND_API_KEY.strip():
        logger.warning("RESEND_API_KEY not set. Cannot fetch email content.")
        return None
    url = f"https://api.resend.com/emails/receiving/{email_id}"
    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.get(url, headers={"Authorization": f"Bearer {RESEND_API_KEY}"})
    except httpx.HTTPError as exc:
        logger.warning("Resend Receiving API request failed: %s", exc)
        return None
    if resp.status_code != 200:
        logger.warning("Resend Receiving API error: %s %s", resp.status_code, resp.text)
        return None
    try:
        return resp.json()
    except json.JSONDecodeError as exc:
        logger.warning("Failed to parse Resend response JSON: %s", exc)
        return None


def _body_contains_buy(email_data: dict) -> bool:
    """True if plain text or HTML body contains the word 'BUY' (case-insensitive)."""
    text = (email_data.get("text") or "").strip()
    html = (email_data.get("html") or "").strip()
    combined = f"{text} {html}"
    return re.search(r"\bbuy\b", combined, flags=re.IGNORECASE) is not None


def _process_buy_reply(email_id: str) -> None:
    """Fetch email, check for BUY, load last digest, append to purchases."""
    email_data = _fetch_received_email(email_id)
    if not email_data:
        return
    if not _body_contains_buy(email_data):
        logger.debug("Email %s does not contain BUY. Ignoring.", email_id)
        return
    last = load_last_digest()
    if not last or "deal" not in last:
        logger.warning("No last_digest.json or missing 'deal'. Cannot log purchase.")
        return
    append_purchase(last["deal"])
    logger.info("BUY reply processed: purchase logged for %s", last["deal"].get("source"))


app = FastAPI(title="Deal Scout Webhook")


@app.post("/webhook/resend")
async def resend_webhook(request: Request, background_tasks: BackgroundTasks) -> Response:
    """
    Resend Inbound: email.received events.
    Return 200 immediately; process BUY reply in background.
    """
    try:
        body = await request.json()
    except (json.JSONDecodeError, ValueError) as exc:
        logger.warning("Invalid webhook body: %s", exc)
        return Response(status_code=200)
    event_type = body.get("type")
    data = body.get("data") or {}
    email_id = data.get("email_id")
    if event_type != "email.received" or not email_id:
        return Response(status_code=200)
    background_tasks.add_task(_process_buy_reply, email_id)
    return Response(status_code=200)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
