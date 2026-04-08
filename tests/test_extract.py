import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.extract_invoice import extract_invoice_fields


def _make_response(text: str):
    msg = MagicMock()
    msg.content = [MagicMock(text=text)]
    return msg


@pytest.mark.asyncio
async def test_valid_json_response():
    payload = {"date": "2024-03-15", "provider": "Acme", "amount": "200.00", "currency": "EUR"}
    with patch("app.extract_invoice.anthropic.AsyncAnthropic") as MockClient:
        instance = MockClient.return_value
        instance.messages.create = AsyncMock(return_value=_make_response(json.dumps(payload)))
        result = await extract_invoice_fields(b"%PDF fake")
    assert result["date"] == "2024-03-15"
    assert result["provider"] == "Acme"
    assert result["amount"] == "200.00"
    assert result["currency"] == "EUR"


@pytest.mark.asyncio
async def test_json_embedded_in_text():
    text = 'Here is the data: {"date":"2024-01-01","provider":"X","amount":"10","currency":"USD"} done.'
    with patch("app.extract_invoice.anthropic.AsyncAnthropic") as MockClient:
        instance = MockClient.return_value
        instance.messages.create = AsyncMock(return_value=_make_response(text))
        result = await extract_invoice_fields(b"%PDF fake")
    assert result["date"] == "2024-01-01"


@pytest.mark.asyncio
async def test_no_json_returns_unknown():
    with patch("app.extract_invoice.anthropic.AsyncAnthropic") as MockClient:
        instance = MockClient.return_value
        instance.messages.create = AsyncMock(return_value=_make_response("I cannot read this."))
        result = await extract_invoice_fields(b"%PDF fake")
    assert all(v == "UNKNOWN" for v in result.values())


@pytest.mark.asyncio
async def test_partial_fields_filled_with_unknown():
    payload = {"date": "2024-05-01", "provider": None, "amount": "", "currency": "GBP"}
    with patch("app.extract_invoice.anthropic.AsyncAnthropic") as MockClient:
        instance = MockClient.return_value
        instance.messages.create = AsyncMock(return_value=_make_response(json.dumps(payload)))
        result = await extract_invoice_fields(b"%PDF fake")
    assert result["date"] == "2024-05-01"
    assert result["provider"] == "UNKNOWN"
    assert result["amount"] == "UNKNOWN"
    assert result["currency"] == "GBP"
