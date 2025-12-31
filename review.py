import streamlit as st
import google.generativeai as genai
from docx import Document
import PyPDF2
import openai

# --- KONFIGURASI TAMPILAN ---
st.set_page_config(page_title="Multi-AI Manuscript Reviewer", page_icon="🔬", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stSelectbox label { font-weight: bold; color: #1f77b4; }
    </style>
    """, unsafe_allow_html=True)

# --- KONFIGURASI API PERMANEN ---
# Masukkan API Key Anda di sini agar tidak perlu mengetik lagi
GEMINI_API_KEY = "MASUKKAN_API_KEY_GEMINI_ANDA_DISINI"

# --- SIDEBAR: PENGATURAN AI ---
with st.sidebar:
    st.title("⚙️ Konfigurasi AI")
    ai_choice = st.selectbox("Pilih Model AI:", ["Gemini Pro (Google)", "GPT-4 (OpenAI)", "DeepSeek V3"])
    
    st.info("Kunci API Gemini sudah terpasang otomatis.")
    # Jika menggunakan model lain, input manual tetap disediakan
    manual_api_key = st.text_input("API Key (untuk GPT-4/DeepSeek):", type="password")

# --- FUNGSI EKSTRAKSI ---
def extract_text(file):
    if file.name.endswith('.docx'):
        doc = Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    elif file.name.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(file)
        return "\n".join([page.extract_text() for page in pdf_reader.pages])
    return None

# --- UI UTAMA ---
st.title("🔬 Advanced Multi-AI Article Reviewer")
st.write("Reviewer otomatis standar Scopus menggunakan model AI terbaik dunia.")
st.write(f"Domain aktif: **analysisidata.co.id**")

uploaded_file = st.file_uploader("Upload Dokumen (PDF/Docx)", type=["pdf", "docx"])

if uploaded_file:
    text = extract_text(uploaded_file)
    
    if st.button("🚀 Jalankan Review Mendalam"):
        # Menentukan API Key mana yang dipakai
        current_key = GEMINI_API_KEY if ai_choice == "Gemini Pro (Google)" else manual_api_key
        
        if not current_key or current_key == "MASUKKAN_API_KEY_GEMINI_ANDA_DISINI":
            st.error("API Key belum disetting dengan benar!")
        else:
            with st.spinner(f"Sedang menganalisis menggunakan {ai_choice}..."):
                prompt = f"Bertindaklah sebagai Reviewer Senior Jurnal Scopus Q1. Berikan laporan detail (Skor 1-100, Kekuatan, Kelemahan, dan Saran Perbaikan) untuk artikel ini:\n\n{text[:15000]}"
                
                try:
                    if ai_choice == "Gemini Pro (Google)":
                        genai.configure(api_key=current_key)
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        response = model.generate_content(prompt).text
                    
                    elif ai_choice == "GPT-4 (OpenAI)":
                        client = openai.OpenAI(api_key=current_key)
                        res = client.chat.completions.create(
                            model="gpt-4",
                            messages=[{"role": "user", "content": prompt}]
                        )
                        response = res.choices[0].message.content
                        
                    elif ai_choice == "DeepSeek V3":
                        client = openai.OpenAI(api_key=current_key, base_url="https://api.deepseek.com")
                        res = client.chat.completions.create(
                            model="deepseek-chat",
                            messages=[{"role": "user", "content": prompt}]
                        )
                        response = res.choices[0].message.content

                    st.subheader(f"Hasil Analisis {ai_choice}:")
                    st.markdown(response)
                    
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {str(e)}")