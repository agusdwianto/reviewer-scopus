# reviewer-scopus
Advanced AI-Powered Scientific Manuscript Reviewer: A Comprehensive Evaluation Tool for Scopus-Indexed Journal Standards using Gemini Pro 6

## Dependencies & setup
- Install Python dependencies: `pip install -r requirements.txt` (includes `reportlab` for Unicode-safe PDF generation).
- Set required environment variables:
  - `GEMINI_API_KEY` - API key for the Gemini/GenAI model (do NOT commit this in source code)
  - `ADMIN_PASSWORD` (optional) - password for admin actions in the sidebar

Notes:
- PDF generation prefers `reportlab` (supports UTF-8 output). If `reportlab` is not installed, the library will fall back to `fpdf2` (latin-1 encoding may drop non-Latin characters).
- The app also supports setting a runtime (session-only) Gemini key via the admin sidebar which takes precedence over the environment variable.
