# Copilot / AI Agent Instructions for reviewer-scopus 🔧

Purpose
- Short: get an AI coding agent productive quickly — this repo is a single-file Streamlit app (`review.py`) that runs a manuscript reviewer using Google Generative AI (Gemini).

Quick start (local / devcontainer) ⚡
- Devcontainer: attaches and auto-runs Streamlit. See `.devcontainer/devcontainer.json` postAttachCommand:
  ```sh
  streamlit run review.py --server.enableCORS false --server.enableXsrfProtection false
  ```
  App is available at port 8501 (forwarded by devcontainer).
- Local run:
  ```sh
  pip install -r requirements.txt
  streamlit run review.py --server.enableCORS false --server.enableXsrfProtection false
  ```

High-level architecture & key files 🏗️
- `review.py` (single-file app):
  - extract_text(file): handles `.docx` (python-docx) and `.pdf` (PyPDF2). Note: PDF pages may return None for images-only pages — add guards.
  - generate_pdf_report(content): uses `FPDF` (from the `fpdf2` package) and encodes text with `latin-1` (may drop Unicode characters).
  - Analysis flow: `genai.configure(api_key=...)` then `genai.GenerativeModel('gemini-1.5-pro')` followed by `model.generate_content(full_prompt).text`.
  - Prompt specifics: language default is **Bahasa Indonesia** and the prompt is truncated with `text_content[:20000]` before sending to the model. The UI preview truncates the response with `response[:1000]`.
- `requirements.txt`: dependency source of truth.
- `.devcontainer/devcontainer.json`: shows how environment runs automatically at attach.

Project-specific patterns & gotchas ✅
- Long, structured prompts: the app expects a numbered output (SUMMARY SCORE, NOVELTY, METHODS, CITATION QUALITY, SECTION-WISE FEEDBACK, FINAL VERDICT).
- Truncation points are intentional and must be updated if you change prompt size: see `{text_content[:20000]}` in `review.py`.
- The `ai_model` selectbox exists in the sidebar but is not used — updating model behavior requires changing the `model = genai.GenerativeModel(...)` line to use `ai_model` (map UI label -> actual model id).
- There was previously a hard-coded API key: **do not commit secrets**.
- `openai` is imported but unused; remove or integrate it intentionally.

Security & environment variables ⚠️
- The app now reads these env vars (set them in Codespaces/Devcontainer or CI):
  - `GEMINI_API_KEY` - required for calling the Google Generative AI API. If missing, analysis is disabled and the UI shows a helpful message.
  - `ADMIN_PASSWORD` - (optional) password to protect the reviewer admin dashboard (export reviewers).
  - `REVIEWERS_DB` - (optional) path to the SQLite DB file (defaults to `data/reviewers.db`).

Example (in shell):

```bash
export GEMINI_API_KEY='sk-...'
export ADMIN_PASSWORD='s3cr3t'
export REVIEWERS_DB='data/reviewers.db'
```

- Use Codespaces/Devcontainer secrets or CI repo secrets for deployment and CI.

Testing suggestions (concrete) 🧪
- Unit tests:
  - `tests/test_extract_text.py`: fixture `tests/fixtures/sample.pdf` and `sample.docx`, test empty-file and images-only PDF behavior.
  - `tests/test_generate_pdf_report.py`: ensure returned value is `bytes` and that encoding doesn't crash on common inputs.
- Integration smoke test:
  - Use `pytest` with `monkeypatch` or `responses` to mock `genai.GenerativeModel` so the full Streamlit flow runs without calling external APIs.

PR checklist for agents 📝
- Remove hard-coded secrets; fail-fast if env var missing.
- Add/update tests for any changed behavior and include fixtures.
- Update `requirements.txt` for new dependencies.
- Preserve the Bahasa Indonesia default unless intentionally changing UX language.
- Document prompt/format changes in `README.md` and this file.

Useful pointers (where to look) 🔎
- Prompt truncation: `review.py` -> `full_prompt` -> `{text_content[:20000]}`
- Secret location: `review.py` -> `GEMINI_API_KEY = "..."`
- Model binding: `review.py` -> `model = genai.GenerativeModel('gemini-1.5-pro')`
- Devcontainer auto-run: `.devcontainer/devcontainer.json` -> `postAttachCommand` (Streamlit command)

Notes & improvements to consider 💡
- Consider switching PDF generation from `FPDF` (latin-1) to a Unicode-friendly library if reports must preserve non-Latin characters.
- Add input validation for `extract_text()` to ignore None pages and to handle large files gracefully (stream or early truncation).

If you'd like, I can:
- Open a PR that removes the hard-coded key and adds env-var validation + tests ✅
- Add test templates and example fixtures ✅

Tell me which follow-up you prefer or which sections need more detail and I will iterate. 🙌