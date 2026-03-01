"""
Unit tests for ai_parser.py
"""
import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from ai_parser import parse_with_claude, parse_with_gemini, parse_with_ollama, parse_deal, SYSTEM_PROMPT, USER_PROMPT_TEMPLATE


@pytest.mark.asyncio
async def test_parse_with_claude_calls_anthropic_correctly():
    """Test that parse_with_claude calls Anthropic with correct system prompt."""
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
    
    with patch('ai_parser.AsyncAnthropic', return_value=mock_client):
        result = await parse_with_claude("<html>test</html>")
    
    # Verify Anthropic was called with correct parameters
    mock_client.messages.create.assert_called_once()
    call_args = mock_client.messages.create.call_args
    assert call_args.kwargs['model'] == "claude-sonnet-4-6"
    assert call_args.kwargs['system'] == SYSTEM_PROMPT
    assert "test" in call_args.kwargs['messages'][0]['content']
    
    # Verify result
    assert result['base_price'] == 1299.99
    assert result['trade_in_value'] == 500.0
    assert result['perks'] == ["Galaxy Buds 4"]


@pytest.mark.asyncio
async def test_parse_deal_returns_none_when_all_backends_fail():
    """Test that parse_deal returns None when all backends raise exceptions."""
    with patch('ai_parser.parse_with_claude', side_effect=Exception("Claude failed")), \
         patch('ai_parser.parse_with_gemini', side_effect=Exception("Gemini failed")), \
         patch('ai_parser.parse_with_ollama', side_effect=Exception("Ollama failed")):
        
        result = await parse_deal("<html>test</html>")
    
    assert result is None


@pytest.mark.asyncio
async def test_parse_deal_falls_through_to_second_backend():
    """Test that parse_deal falls through to second backend when first raises."""
    mock_result = {
        "base_price": 1299.99,
        "trade_in_value": 0.0,
        "perks": [],
        "pickup_available": False,
        "urgent": False,
        "urgency_deadline": None,
    }
    
    with patch('ai_parser.parse_with_claude', side_effect=Exception("Claude failed")), \
         patch('ai_parser.parse_with_gemini', return_value=mock_result), \
         patch('ai_parser.parse_with_ollama') as mock_ollama:
        
        result = await parse_deal("<html>test</html>")
    
    assert result == mock_result
    # Ollama should not be called since Gemini succeeded
    mock_ollama.assert_not_called()


@pytest.mark.asyncio
async def test_parse_with_gemini_strips_markdown_fences():
    """Test that Gemini response with markdown fences is properly cleaned."""
    mock_response = MagicMock()
    mock_response.text = "```json\n" + json.dumps({
        "base_price": 1299.99,
        "trade_in_value": 500.0,
        "perks": [],
        "pickup_available": True,
        "urgent": False,
        "urgency_deadline": None,
    }) + "\n```"
    
    mock_model = AsyncMock()
    mock_model.generate_content_async = AsyncMock(return_value=mock_response)
    
    with patch('ai_parser.genai') as mock_genai:
        mock_genai.configure = MagicMock()
        mock_genai.GenerativeModel = MagicMock(return_value=mock_model)
        
        result = await parse_with_gemini("<html>test</html>")
    
    assert result['base_price'] == 1299.99
    assert result['trade_in_value'] == 500.0


@pytest.mark.asyncio
async def test_parse_with_ollama_strips_markdown_fences():
    """Test that Ollama response with markdown fences is properly cleaned."""
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
    
    async def mock_context_manager():
        return mock_client
    
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)
        
        result = await parse_with_ollama("<html>test</html>")
    
    assert result['base_price'] == 1299.99
    assert result['perks'] == ["Galaxy Buds 4"]


@pytest.mark.asyncio
async def test_parse_deal_returns_dict_with_required_keys():
    """Test that parse_deal always returns dict with required keys."""
    mock_result = {
        "base_price": 1299.99,
        "trade_in_value": 500.0,
        "perks": ["Galaxy Buds 4"],
        "pickup_available": True,
        "urgent": False,
        "urgency_deadline": None,
    }
    
    with patch('ai_parser.parse_with_claude', return_value=mock_result):
        result = await parse_deal("<html>test</html>")
    
    assert result is not None
    assert 'base_price' in result
    assert 'trade_in_value' in result
    assert 'perks' in result
    assert 'pickup_available' in result
    assert isinstance(result['perks'], list)

