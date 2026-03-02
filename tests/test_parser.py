"""
Unit tests for ai_parser.py
"""
import asyncio
import json
from unittest.mock import AsyncMock, patch, MagicMock
from ai_parser import (
    _strip_markdown_json,
    parse_with_claude,
    parse_with_gemini,
    parse_with_ollama,
    parse_deal,
    SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE,
)


def test_parse_with_claude_calls_anthropic_correctly():
    """Test that parse_with_claude calls Anthropic with correct system prompt."""
    async def run():
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps({
            "base_price": 1299.99,
            "trade_in_value": 500.0,
            "perks": ["Galaxy Buds 4"],
            "pickup_available": True,
            "urgent": False,
            "urgency_deadline": None,
        }))]

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with patch('anthropic.AsyncAnthropic', return_value=mock_client):
            result = await parse_with_claude("<html>test</html>")

        mock_client.messages.create.assert_called_once()
        call_args = mock_client.messages.create.call_args
        assert call_args.kwargs['model'] == "claude-sonnet-4-6"
        assert call_args.kwargs['system'] == SYSTEM_PROMPT
        assert "test" in call_args.kwargs['messages'][0]['content']

        assert result['base_price'] == 1299.99
        assert result['trade_in_value'] == 500.0
        assert result['perks'] == ["Galaxy Buds 4"]

    asyncio.run(run())


def test_parse_deal_returns_none_when_all_backends_fail():
    """Test that parse_deal returns None when all backends raise exceptions."""
    async def run():
        with patch('ai_parser.parse_with_claude', side_effect=Exception("Claude failed")), \
             patch('ai_parser.parse_with_gemini', side_effect=Exception("Gemini failed")), \
             patch('ai_parser.parse_with_ollama', side_effect=Exception("Ollama failed")):
            result = await parse_deal("<html>test</html>")
        assert result is None

    asyncio.run(run())


def test_parse_deal_falls_through_to_second_backend():
    """Test that parse_deal falls through to second backend when first raises."""
    mock_result = {
        "base_price": 1299.99,
        "trade_in_value": 0.0,
        "perks": [],
        "pickup_available": False,
        "urgent": False,
        "urgency_deadline": None,
    }

    async def run():
        with patch('ai_parser.parse_with_claude', side_effect=Exception("Claude failed")), \
             patch('ai_parser.parse_with_gemini', new_callable=AsyncMock, return_value=mock_result), \
             patch('ai_parser.parse_with_ollama') as mock_ollama:
            result = await parse_deal("<html>test</html>")
        assert result == mock_result
        mock_ollama.assert_not_called()

    asyncio.run(run())


def test_strip_markdown_json_removes_fences():
    """Test that LLM response with markdown fences is properly cleaned (used by Gemini and Ollama)."""
    raw = "```json\n" + json.dumps({
        "base_price": 1299.99,
        "trade_in_value": 500.0,
        "perks": [],
        "pickup_available": True,
        "urgent": False,
        "urgency_deadline": None,
    }) + "\n```"
    stripped = _strip_markdown_json(raw)
    parsed = json.loads(stripped)
    assert parsed["base_price"] == 1299.99
    assert parsed["trade_in_value"] == 500.0


def test_parse_with_ollama_strips_markdown_fences():
    """Test that Ollama response with markdown fences is properly cleaned."""
    async def run():
        mock_response = MagicMock()
        mock_response.json = MagicMock(return_value={
            "response": "```json\n" + json.dumps({
                "base_price": 1299.99,
                "trade_in_value": 0.0,
                "perks": ["Galaxy Buds 4"],
                "pickup_available": False,
                "urgent": False,
                "urgency_deadline": None,
            }) + "\n```"
        })

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)
            result = await parse_with_ollama("<html>test</html>")

        assert result['base_price'] == 1299.99
        assert result['perks'] == ["Galaxy Buds 4"]

    asyncio.run(run())


def test_parse_deal_returns_dict_with_required_keys():
    """Test that parse_deal always returns dict with required keys."""
    mock_result = {
        "base_price": 1299.99,
        "trade_in_value": 500.0,
        "perks": ["Galaxy Buds 4"],
        "pickup_available": True,
        "urgent": False,
        "urgency_deadline": None,
    }

    async def run():
        with patch('ai_parser.parse_with_claude', new_callable=AsyncMock, return_value=mock_result):
            result = await parse_deal("<html>test</html>")
        assert result is not None
        assert 'base_price' in result
        assert 'trade_in_value' in result
        assert 'perks' in result
        assert 'pickup_available' in result
        assert isinstance(result['perks'], list)

    asyncio.run(run())

