from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import tempfile
import os

from app.extract_invoice import extract_invoice_fields
from app.build_filename import build_filename
from app.zip_files import build_zip

load_dotenv()

app = FastAPI()

MAX_FILES = 10
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@app.get("/", response_class=HTMLResponse)
async def index():
    with open("static/index.html") as f:
        return f.read()


@app.post("/upload")
async def upload(files: list[UploadFile] = File(...)):
    if len(files) > MAX_FILES:
        raise HTTPException(status_code=400, detail=f"Too many files. Maximum is {MAX_FILES}.")

    renamed = []
    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"'{file.filename}' is not a PDF.")

        contents = await file.read()

        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"'{file.filename}' exceeds 5 MB limit.")

        fields = await extract_invoice_fields(contents)
        new_name = build_filename(fields)
        renamed.append((new_name, contents))

    zip_bytes = build_zip(renamed)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
        tmp.write(zip_bytes)
        tmp_path = tmp.name

    return FileResponse(
        tmp_path,
        media_type="application/zip",
        filename="invoices.zip",
        background=_cleanup(tmp_path),
    )


class _cleanup:
    def __init__(self, path: str):
        self.path = path

    async def __call__(self):
        try:
            os.unlink(self.path)
        except OSError:
            pass


app.mount("/static", StaticFiles(directory="static"), name="static")
