# Invoice Renamer — Web App

## What this app does
Users upload 1–10 PDF invoices via browser. The app extracts
date, provider, amount and currency using Claude vision, then
returns a .zip of renamed files.

Output filename: `YYYY_MM_DD PROVIDER_NAME AMOUNT CURRENCY.pdf`

## Stack
- FastAPI — backend + API routes
- Anthropic SDK (Python) — claude-sonnet-4-20250514, vision for PDF parsing
- PyMuPDF or pdfplumber — PDF handling
- zipfile (stdlib) — zip file generation
- Vercel — hosting via vercel.json config (connected to GitHub, auto-deploy on push)
- GitHub — source control

## Project structure
app/
  main.py              ← FastAPI app + upload endpoint
  extract_invoice.py   ← Claude API call + field parsing
  build_filename.py    ← filename sanitization logic
  zip_files.py         ← zip assembly
static/
  index.html           ← upload UI (vanilla HTML/JS)
tests/
  test_extract.py
  test_filename.py
  test_api.py
requirements.txt
.env                   ← ANTHROPIC_API_KEY (gitignored)
.gitignore             ← must include .env
vercel.json            ← routes Python app via WSGI

## Constraints (enforce always)
- Accept ONLY .pdf files — reject all others with clear UI error
- Max file size: 5MB per file — reject with clear UI error
- Max files per upload: 10 — reject extras with clear UI error
- NEVER log or store uploaded files server-side
- NEVER expose ANTHROPIC_API_KEY to the client
- robots.txt must disallow all crawlers (noindex, nofollow)
- If a field can't be extracted: use UNKNOWN as placeholder
- Sanitize filenames: replace spaces with underscores, strip special chars

## API key
Store in .env as ANTHROPIC_API_KEY=sk-...
Load server-side only via python-dotenv: load_dotenv()
In Vercel: add via Dashboard → Project Settings → Environment Variables

## Git rules
- Commit often with clear messages
- .env must be in .gitignore before first commit
- Never commit secrets or uploaded files

## Testing
Run: `pytest`
Cover: field extraction, filename sanitization, error handling,
file type/size/count validation, zip output integrity

## Future (not now)
- User-selectable naming convention
