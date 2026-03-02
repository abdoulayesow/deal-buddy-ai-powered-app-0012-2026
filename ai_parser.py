"""
AI-based HTML parser. Fallback only — called when CSS selectors fail.
Backend priority: claude → gemini → ollama
"""
import json
import logging
import os
import httpx
import anthropic
from config import (
    PARSER_BACKEND, ANTHROPIC_API_KEY,
    GEMINI_API_KEY, OLLAMA_BASE_URL, OLLAMA_MODEL
)

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a precise data extraction agent for e-commerce HTML.
Return ONLY valid JSON. No explanation. No markdown fences. No extra fields."""

USER_PROMPT_TEMPLATE = """
Extract from this HTML snippet:
- base_price (float, USD, required)
- trade_in_value (float, USD, 0.0 if not found)
- perks (list of strings, [] if none)
- pickup_available (bool)
- urgent (bool, true if offer has an expiry deadline)
- urgency_deadline (string or null)

HTML (first 12000 chars):
{html}
"""


def _strip_markdown_json(text: str) -> str:
    """Strip markdown code fences (e.g. ```json ... ```) from LLM response text."""
    return text.strip().lstrip("```json").rstrip("```").strip()


async def parse_with_claude(html: str) -> dict:
    client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": USER_PROMPT_TEMPLATE.format(html=html[:12000])}]
    )
    return json.loads(response.content[0].text)


async def parse_with_gemini(html: str) -> dict:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    prompt = SYSTEM_PROMPT + "\n\n" + USER_PROMPT_TEMPLATE.format(html=html[:12000])
    response = await model.generate_content_async(prompt)
    return json.loads(_strip_markdown_json(response.text))


async def parse_with_ollama(html: str) -> dict:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": SYSTEM_PROMPT + "\n\n" + USER_PROMPT_TEMPLATE.format(html=html[:8000]),
                "stream": False,
            }
        )
        result = response.json()
        return json.loads(_strip_markdown_json(result["response"]))


async def parse_deal(html: str) -> dict | None:
    """
    Try each backend in priority order.
    Returns parsed dict or None if all backends fail.
    """
    backends = {
        "claude": parse_with_claude,
        "gemini": parse_with_gemini,
        "ollama": parse_with_ollama,
    }

    # Always start with configured backend, then fall through
    order = [PARSER_BACKEND] + [k for k in backends if k != PARSER_BACKEND]

    for backend_name in order:
        try:
            logger.info(f"AI parser attempting backend: {backend_name}")
            result = await backends[backend_name](html)
            logger.info(f"AI parser succeeded with backend: {backend_name}")
            return result
        except Exception as e:
            logger.warning(f"AI parser backend {backend_name} failed: {e}")
            continue

    logger.error("All AI parser backends failed.")
    return None

