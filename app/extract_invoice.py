import base64
import json
import os
import re

import anthropic

MODEL = "claude-sonnet-4-20250514"

SYSTEM_PROMPT = """You are an invoice data extractor. Given a PDF invoice, extract:
- date: invoice date in YYYY-MM-DD format
- provider: name of the company or person issuing the invoice
- amount: numeric amount (e.g. 123.45)
- currency: 3-letter ISO currency code (e.g. EUR, USD, GBP)

Respond ONLY with a JSON object with keys: date, provider, amount, currency.
If a field cannot be determined, use the string "UNKNOWN".
Example: {"date": "2024-03-15", "provider": "Acme Corp", "amount": "450.00", "currency": "EUR"}"""


async def extract_invoice_fields(pdf_bytes: bytes) -> dict:
    client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    pdf_b64 = base64.standard_b64encode(pdf_bytes).decode("utf-8")

    message = await client.messages.create(
        model=MODEL,
        max_tokens=256,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_b64,
                        },
                    },
                    {"type": "text", "text": "Extract the invoice fields."},
                ],
            }
        ],
    )

    raw = message.content[0].text
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return {"date": "UNKNOWN", "provider": "UNKNOWN", "amount": "UNKNOWN", "currency": "UNKNOWN"}

    try:
        data = json.loads(match.group())
    except json.JSONDecodeError:
        return {"date": "UNKNOWN", "provider": "UNKNOWN", "amount": "UNKNOWN", "currency": "UNKNOWN"}

    return {
        "date": data.get("date") or "UNKNOWN",
        "provider": data.get("provider") or "UNKNOWN",
        "amount": data.get("amount") or "UNKNOWN",
        "currency": data.get("currency") or "UNKNOWN",
    }
