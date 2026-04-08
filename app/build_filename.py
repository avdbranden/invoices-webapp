import re


DEFAULT_FIELD_ORDER = ["date", "provider", "amount"]

_SANITIZERS = {
    "date": lambda v: _sanitize_date(v),
    "provider": lambda v: _sanitize_provider(v),
    "amount": lambda v: _sanitize_amount(v),
    "currency": lambda v: _sanitize_token(v),
}


def build_filename(fields: dict, field_order: list[str] | None = None) -> str:
    """Build output filename from extracted fields in the given order."""
    if not field_order:
        field_order = DEFAULT_FIELD_ORDER

    parts = []
    for key in field_order:
        sanitize = _SANITIZERS.get(key)
        if sanitize:
            parts.append(sanitize(fields.get(key, "UNKNOWN")))

    return " ".join(parts) + ".pdf"


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
