import io
import zipfile
import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport

from app.main import app

FAKE_FIELDS = {"date": "2024-03-15", "provider": "Acme", "amount": "100.00", "currency": "EUR"}
FAKE_PDF = b"%PDF-1.4 fake pdf content"


@pytest.fixture
def pdf_file():
    return ("files", ("invoice.pdf", io.BytesIO(FAKE_PDF), "application/pdf"))


@pytest.mark.asyncio
async def test_upload_returns_zip(pdf_file):
    with patch("app.main.extract_invoice_fields", new_callable=AsyncMock, return_value=FAKE_FIELDS):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/upload", files=[pdf_file])
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    zf = zipfile.ZipFile(io.BytesIO(response.content))
    assert len(zf.namelist()) == 1
    assert zf.namelist()[0].endswith(".pdf")


@pytest.mark.asyncio
async def test_rejects_non_pdf():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/upload",
            files=[("files", ("document.txt", io.BytesIO(b"text"), "text/plain"))],
        )
    assert response.status_code == 400
    assert "not a PDF" in response.json()["detail"]


@pytest.mark.asyncio
async def test_rejects_too_many_files():
    files = [("files", (f"inv{i}.pdf", io.BytesIO(FAKE_PDF), "application/pdf")) for i in range(11)]
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/upload", files=files)
    assert response.status_code == 400
    assert "Too many files" in response.json()["detail"]


@pytest.mark.asyncio
async def test_rejects_oversized_file():
    big = b"%PDF " + b"x" * (5 * 1024 * 1024 + 1)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/upload",
            files=[("files", ("big.pdf", io.BytesIO(big), "application/pdf"))],
        )
    assert response.status_code == 400
    assert "5 MB" in response.json()["detail"]


@pytest.mark.asyncio
async def test_zip_contains_correct_filename(pdf_file):
    with patch("app.main.extract_invoice_fields", new_callable=AsyncMock, return_value=FAKE_FIELDS):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/upload", files=[pdf_file])
    zf = zipfile.ZipFile(io.BytesIO(response.content))
    assert zf.namelist()[0] == "2024_03_15 Acme 100.00 EUR.pdf"
