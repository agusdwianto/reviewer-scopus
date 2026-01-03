import os
import streamlit as st
import google.generativeai as genai
from docx import Document
import PyPDF2
import pandas as pd
import datetime

from reviewer_db import init_db, add_reviewer, list_reviewers, export_csv_bytes

# --- CONFIG ---
st.set_page_config(page_title="Professional AI Manuscript Reviewer", page_icon="⚖️", layout="wide")

# Database path (override via REVIEWERS_DB env var)
DB_PATH = os.environ.get('REVIEWERS_DB', 'data/reviewers.db')
init_db(DB_PATH)

# GEMINI API key via env var (do NOT commit secrets)
# For public deployments, set GEMINI_API_KEY in the server environment or use the admin runtime key (session-only).
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
# Admin password (optional) configured via ADMIN_PASSWORD env var
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
# Allow public (no per-user API key prompts). Set to 'false' to require admin-only access.
ALLOW_PUBLIC = os.environ.get('ALLOW_PUBLIC', 'true').lower() == 'true'


def get_api_key():
    """Return runtime key (set by admin in session) or environment key if available."""
    return st.session_state.get('runtime_gemini_key') or os.environ.get('GEMINI_API_KEY')


# UI Enhancement
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .report-card { background-color: white; padding: 25px; border-radius: 15px; border-top: 5px solid #003366; }
    </style>
    """, unsafe_allow_html=True)

# --- API SETUP ---
# Do NOT hard-code the GEMINI API key here. It should be provided via the
# environment variable `GEMINI_API_KEY` or set at runtime by an admin in the
# sidebar (stored only for the session).
# The effective key used for analysis is returned by `get_api_key()`.

# --- SIDEBAR ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'admin_authenticated' not in st.session_state:
    st.session_state['admin_authenticated'] = False

with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>SYSTEM CONTROL</h2>", unsafe_allow_html=True)
    st.image("https://analysisidata.co.id/wp-content/uploads/2023/01/logo-dummy.png", use_container_width=True)
    if GEMINI_API_KEY:
        st.success("✅ Gemini AI: Configured")
    else:
        st.warning("⚠️ GEMINI_API_KEY not configured. Analysis disabled until admin sets it as env var.")

    st.markdown("---")

    # Admin login (protected by ADMIN_PASSWORD env var)
    if ADMIN_PASSWORD:
        if not st.session_state['admin_authenticated']:
            pwd = st.text_input('Admin password', type='password')
            if st.button('Admin Login'):
                if pwd == ADMIN_PASSWORD:
                    st.session_state['admin_authenticated'] = True
                    st.success('Admin authenticated')
                else:
                    st.error('Invalid admin password')
        else:
            st.success('Admin: signed in')
            if st.button('Sign out admin'):
                st.session_state['admin_authenticated'] = False

    st.markdown('---')

    if st.session_state['admin_authenticated']:
        st.markdown('### Reviewer Database')
        if st.button('Export reviewers (CSV)'):
            csv_bytes = export_csv_bytes(DB_PATH)
            st.download_button('Download CSV', csv_bytes, 'reviewers.csv', 'text/csv')
        reviewers = list_reviewers(DB_PATH)
        st.write(f'Count: {len(reviewers)}')

        with st.expander('Admin: Configure Service'):
            st.write('Runtime key is stored only for the active server session and not persisted.')
            env_status = 'set' if os.environ.get('GEMINI_API_KEY') else 'not set'
            st.write(f'Env GEMINI_API_KEY: {env_status}')
            key_input = st.text_input('Set runtime Gemini API key (runtime only)', type='password', key='admin_runtime_key')
            if st.button('Set Runtime Key', key='set_runtime_key'):
                if key_input.strip():
                    st.session_state['runtime_gemini_key'] = key_input.strip()
                    st.success('Runtime key set for this session')
            if st.session_state.get('runtime_gemini_key'):
                if st.button('Clear Runtime Key', key='clear_runtime_key'):
                    st.session_state.pop('runtime_gemini_key', None)
                    st.success('Runtime key cleared')

            # Allow public toggle (session-only)
            public_toggle = st.checkbox('Allow public access (no API key entry by users)', value=ALLOW_PUBLIC, key='allow_public')
            st.write('Public mode:', 'Enabled' if public_toggle else 'Disabled')
            st.write('Tip: For production, set `GEMINI_API_KEY` as an environment variable on the server and use `ADMIN_PASSWORD` to protect admin actions.')

    else:
        st.info('Need an account? Register first on the main page.')

    ai_model = st.selectbox('Select Intelligence Engine:', ['Gemini 1.5 Pro (Ultra Precision)', 'GPT-4 Turbo'])

# --- FUNCTIONS (moved to utils) ---
from utils import extract_text, file_too_large, generate_pdf_report

# NOTE: `generate_pdf_report` moved to `utils.py` to isolate the `fpdf` dependency
# and make it import-safe (so importing modules that depend on this package
# doesn't fail when `fpdf` is not installed). See `utils.generate_pdf_report`.

# --- MAIN INTERFACE ---
# Registration flow: users must register before using the review tool
if not st.session_state.get('authenticated'):
    st.title('🎓 Researcher Registration')
    st.write('Silakan daftar untuk menggunakan layanan Reviewer AI (gratis).')
    with st.form('reg_form'):
        name = st.text_input('Nama Lengkap & Gelar')
        email = st.text_input('Email Institusi')
        affiliation = st.text_input('Afiliasi / Universitas')
        orcid = st.text_input('ORCID (opsional)')
        keywords = st.text_input('Bidang Keahlian (kata kunci, pisahkan koma)')
        submitted = st.form_submit_button('Daftar & Mulai Review')
        if submitted:
            if not (name and email):
                st.error('Nama dan Email wajib diisi.')
            else:
                add_reviewer(DB_PATH, name=name, email=email, affiliation=affiliation, orcid=orcid, keywords=keywords)
                st.session_state['authenticated'] = True
                st.session_state['user_name'] = name
                st.success('Pendaftaran berhasil. Selamat datang, ' + name)
                st.experimental_rerun()

else:
    st.title("⚖️ Professional Peer-Review AI Portal")
    st.subheader("Academic validation & deep analysis based on Scopus Content Selection criteria.")
    st.write(f"Signed in as **{st.session_state.get('user_name')}**")
    if st.button('Log out'):
        st.session_state['authenticated'] = False
        st.experimental_rerun()

    uploaded_file = st.file_uploader("Drop your manuscript here (PDF/DOCX)", type=["pdf", "docx"])

    if uploaded_file:
        text_content = extract_text(uploaded_file)
        
        if st.button("START COMPREHENSIVE REVIEW"):
            # Check API key availability (runtime key overrides env var)
            api_key = get_api_key()
            if not api_key:
                st.error('Analysis is disabled: GEMINI_API_KEY (env or runtime) is not set. Contact admin to configure the server environment variable or set a runtime key.')
            else:
                with st.spinner("Executing multi-dimensional analysis..."):
                    # Prompt yang jauh lebih teknis dan detail
                    full_prompt = f"""
                    As a Senior Editor of a Q1 Scopus Journal, provide a rigorous review for this manuscript:
                    
                    1. SUMMARY SCORE (0-100)
                    2. NOVELTY ANALYSIS: What is the unique contribution?
                    3. METHODOLOGICAL RIGOR: Is the methodology sound and reproducible?
                    4. CITATION QUALITY: Are references recent and from high-impact sources?
                    5. SYSTEMATIC FEEDBACK: Section-by-section improvements (Title, Abstract, Results, Discussion).
                    6. FINAL VERDICT: (Accept, Minor Revision, Major Revision, or Reject).

                    Format the output with clear headers and bullet points.
                    Language: Bahasa Indonesia (Formal Academic).

                    Manuscript Content:
                    {text_content[:20000]}
                    """
                    
                    try:
                        # Compute simple deterministic scores based on manuscript content
                        from scoring import score_manuscript
                        scores = score_manuscript(text_content)

                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel('gemini-1.5-pro')
                        response = model.generate_content(full_prompt).text
                        
                        # --- DISPLAY RESULTS (DASHBOARD STYLE) ---
                        st.markdown("---")
                        m1, m2, m3 = st.columns(3)
                        m1.metric("Total Score", f"{scores['Total']}/100")
                        m2.metric("Novelty", f"{scores['Originality']}/20")
                        m3.metric("Methodology", f"{scores['Methodology']}/20")

                        # Tabs for organized view
                        tab1, tab2, tab3 = st.tabs(["📊 Executive Summary", "🔍 Deep Analysis", "📝 Revision Guide"])
                        
                        with tab1:
                            st.markdown(f"<div class='report-card'>{response[:1000]}...</div>", unsafe_allow_html=True)
                            st.markdown("**Score breakdown**")
                            st.write({k: v for k, v in scores.items() if k != 'Total'})
                        
                        with tab2:
                            st.write(response)
                        
                        with tab3:
                            st.warning("Action Required: Perkuat bagian diskusi dan sinkronisasi data pada tabel 2.")

                        # DOWNLOAD SECTION
                        st.markdown("### 🖨️ Export Official Report")
                        pdf_bytes = generate_pdf_report(response, st.session_state.get('user_name'), scores=scores)
                        st.download_button(
                            label="Download Professional Review Report (PDF)",
                            data=pdf_bytes,
                            file_name="Scopus_Review_Report.pdf",
                            mime="application/pdf"
                        )

                    except Exception as e:
                        st.error(f"Analysis Error: {e}")

# --- FOOTER ---
st.markdown("---")
st.caption("© 2025 analysisidata.co.id - Scopus Q1 Standards Applied.")