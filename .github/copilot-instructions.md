# Copilot / AI Agent Instructions for reviewer-scopus 🔧

Purpose
- Short: help an AI coding agent be immediately productive with this repository — a single-file Streamlit app (`review.py`) that runs a manuscript reviewer using Gemini/Google generative APIs.

Quick start (local / devcontainer) ⚡
- Devcontainer: this repository auto-runs Streamlit on attach. See `.devcontainer/devcontainer.json` `postAttachCommand` (runs `streamlit run review.py --server.enableCORS false --server.enableXsrfProtection false`). Port 8501 is forwarded.
- Local: install deps and run the app:
  - pip install -r requirements.txt
  - streamlit run review.py

High-level architecture & major components 🏗️
- Single-page Streamlit app: `review.py` is the entire application.
  - UI: Streamlit controls, `st.sidebar` for model selection and `st.file_uploader` for manuscripts.
  - Extraction: `extract_text(file)` supports `.docx` (python-docx) and `.pdf` (PyPDF2).
  - Analysis: uses `google-generativeai` (`genai.configure` + `genai.GenerativeModel('gemini-1.5-pro')`) and builds a long `full_prompt` (language set to Bahasa Indonesia by default). The prompt is explicitly truncated to the first ~20k chars of the manuscript.
  - Output & report: response is shown in multiple tabs and can be exported via `generate_pdf_report()` (FPDF, latin-1 encoding). `st.download_button` serves the generated PDF.

Project-specific conventions & patterns ✅
- Prompts are long, structured, and numbered; expect the app to ask for: score, novelty, methods, citations, section-wise feedback, final verdict.
- The displayed preview truncates the response (`response[:1000]...`) while tab 2 shows the full text.
- UI assumes Bahasa Indonesia formal academic language for feedback — preserve that unless intentionally changing the UX.
- `ai_model` selectbox exists but the integration currently always uses Gemini (`gemini-1.5-pro`) — an agent changing models should update the call-site accordingly.

Security & secret handling ⚠️
- Current code contains a hard-coded API key: `GEMINI_API_KEY = "AIzaSyB..."`. **Do not commit keys**. Replace with an env var (example):

```py
import os
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise RuntimeError('GEMINI_API_KEY env var required')
```

- Use Codespaces/Devcontainer secrets or CI secrets for protected environments.

Files to look at first 🔎
- `review.py` — primary source of truth (prompt logic, IO, UI layout)
- `requirements.txt` — dependencies to update when adding libs
- `.devcontainer/devcontainer.json` — how the environment is launched (auto-run Streamlit)
- `README.md` — short project description

Testing & small tasks that are straightforward to automate 🧪
- Unit-test `extract_text()` for both sample PDF and DOCX files (create `tests/fixtures/sample.pdf` and `.docx`). Ensure edge cases (empty file, images-only PDF) are handled gracefully.
- Unit-test `generate_pdf_report()` returns bytes and that `latin-1` encoding doesn't crash for basic Unicode inputs.
- Add a simple integration smoke test that runs the Streamlit script with a small fixture and ensures the analysis path is exercised (mock external API calls).

Operator / Debugging tips 🐞
- Streamlit logs and exceptions are visible in the terminal where `streamlit run` is executed.
- Devcontainer auto-starts Streamlit; to reproduce the same behavior locally, use the same flags shown in `.devcontainer/devcontainer.json`.
- Check for unused imports (e.g. `openai` appears unused) and remove or use intentionally.

PR checklist for agents (quick) 📝
- No secrets committed
- Add/update tests for behavior you modify
- Update `requirements.txt` for any new dependency
- Keep default UX (Bahasa Indonesia) unless explicitly changing language
- Document any prompt/format changes in `README.md` or this file

Examples (concrete pointers inside the repository) 📌
- Where to change prompt truncation: inside `review.py` in the block that builds `full_prompt` (it uses `{text_content[:20000]}`).
- Where to fix secrets: replace `GEMINI_API_KEY = "..."` with environment var access.
- Where the app binds to the model: `model = genai.GenerativeModel('gemini-1.5-pro')` in `review.py`.

If anything is unclear or you want me to expand a section (e.g., add test templates, provide a secrets-removal patch, or implement env var usage + tests), tell me which area to focus on and I will iterate. 🙌