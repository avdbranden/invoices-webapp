import re


def build_filename(fields: dict) -> str:
    """Build output filename: YYYY_MM_DD PROVIDER_NAME AMOUNT CURRENCY.pdf"""
    date = _sanitize_date(fields.get("date", "UNKNOWN"))
    provider = _sanitize_provider(fields.get("provider", "UNKNOWN"))
    amount = _sanitize_amount(fields.get("amount", "UNKNOWN"))
    currency = _sanitize_token(fields.get("currency", "UNKNOWN"))

    return f"{date} {provider} {amount} {currency}.pdf"


def _sanitize_date(date: str) -> str:
    if not date or date == "UNKNOWN":
        return "UNKNOWN"
    # Expect YYYY-MM-DD; replace hyphens with underscores
    cleaned = re.sub(r"[^\d\-]", "", date)
    if re.match(r"^\d{4}-\d{2}-\d{2}$", cleaned):
        return cleaned.replace("-", "_")
    return "UNKNOWN"


def _sanitize_provider(provider: str) -> str:
    if not provider or provider == "UNKNOWN":
        return "UNKNOWN"
    # Strip special chars, replace whitespace with underscores
    cleaned = re.sub(r"[^\w\s]", "", provider, flags=re.UNICODE)
    cleaned = re.sub(r"\s+", "_", cleaned.strip())
    cleaned = re.sub(r"_+", "_", cleaned)
    return cleaned or "UNKNOWN"


def _sanitize_amount(amount: str) -> str:
    if not amount or amount == "UNKNOWN":
        return "UNKNOWN"
    # Keep digits and decimal point only
    cleaned = re.sub(r"[^\d.]", "", str(amount))
    return cleaned or "UNKNOWN"


def _sanitize_token(value: str) -> str:
    if not value or value == "UNKNOWN":
        return "UNKNOWN"
    cleaned = re.sub(r"[^\w]", "", value).upper()
    return cleaned or "UNKNOWN"
