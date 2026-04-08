import pytest
from app.build_filename import build_filename


def test_normal_fields_default_order():
    fields = {"date": "2024-03-15", "provider": "Acme Corp", "amount": "450.00", "currency": "EUR"}
    assert build_filename(fields) == "2024_03_15 Acme_Corp 450.00.pdf"


def test_custom_field_order():
    fields = {"date": "2024-03-15", "provider": "Acme", "amount": "450.00", "currency": "EUR"}
    assert build_filename(fields, ["provider", "amount", "date"]) == "Acme 450.00 2024_03_15.pdf"


def test_single_field():
    fields = {"date": "2024-03-15", "provider": "Acme", "amount": "450.00", "currency": "EUR"}
    assert build_filename(fields, ["provider"]) == "Acme.pdf"


def test_currency_included_when_in_order():
    fields = {"date": "2024-03-15", "provider": "Acme", "amount": "450.00", "currency": "EUR"}
    assert build_filename(fields, ["date", "provider", "amount", "currency"]) == "2024_03_15 Acme 450.00 EUR.pdf"


def test_unknown_fields():
    fields = {"date": "UNKNOWN", "provider": "UNKNOWN", "amount": "UNKNOWN", "currency": "UNKNOWN"}
    assert build_filename(fields, ["date", "provider", "amount", "currency"]) == "UNKNOWN UNKNOWN UNKNOWN UNKNOWN.pdf"


def test_missing_fields():
    assert build_filename({}, ["date", "provider", "amount"]) == "UNKNOWN UNKNOWN UNKNOWN.pdf"


def test_special_chars_in_provider():
    fields = {"date": "2024-01-01", "provider": "O'Brien & Sons, Ltd.", "amount": "100", "currency": "USD"}
    name = build_filename(fields)
    assert "&" not in name
    assert "'" not in name
    assert "," not in name
    assert "." not in name or name.endswith(".pdf")


def test_spaces_replaced_with_underscores_in_provider():
    fields = {"date": "2024-06-01", "provider": "My Provider Inc", "amount": "99.99", "currency": "GBP"}
    name = build_filename(fields)
    assert "My_Provider_Inc" in name


def test_invalid_date_format():
    fields = {"date": "15/03/2024", "provider": "X", "amount": "10", "currency": "EUR"}
    name = build_filename(fields)
    assert name.startswith("UNKNOWN ")


def test_amount_strips_non_numeric():
    fields = {"date": "2024-01-01", "provider": "X", "amount": "$1,234.56", "currency": "USD"}
    name = build_filename(fields)
    assert "1234.56" in name


def test_currency_uppercased():
    fields = {"date": "2024-01-01", "provider": "X", "amount": "10", "currency": "eur"}
    name = build_filename(fields, ["date", "provider", "amount", "currency"])
    assert "EUR" in name
