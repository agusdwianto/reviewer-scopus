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

# --- SIDEBAR: PENGATURAN API ---
with st.sidebar:
    st.title("⚙️ Konfigurasi AI")
    ai_choice = st.selectbox("Pilih Model AI:", ["Gemini Pro (Google)", "GPT-4 (OpenAI)", "DeepSeek V3"])
    
    st.info("Masukkan API Key sesuai model yang dipilih:")
    api_key_input = st.text_input("API Key:", type="password")

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

uploaded_file = st.file_uploader("Upload Dokumen (PDF/Docx)", type=["pdf", "docx"])

if uploaded_file:
    text = extract_text(uploaded_file)
    
    if st.button("🚀 Jalankan Review Mendalam"):
        if not api_key_input:
            st.error("Silakan masukkan API Key di sidebar terlebih dahulu!")
        else:
            with st.spinner(f"Sedang menganalisis menggunakan {ai_choice}..."):
                prompt = f"Bertindaklah sebagai Reviewer Senior Jurnal Scopus Q1. Berikan laporan detail (Skor 1-100, Kekuatan, Kelemahan, dan Saran Perbaikan) untuk artikel ini:\n\n{text[:15000]}"
                
                try:
                    if ai_choice == "Gemini Pro (Google)":
                        genai.configure(api_key=api_key_input)
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        response = model.generate_content(prompt).text
                    
                    elif ai_choice == "GPT-4 (OpenAI)":
                        client = openai.OpenAI(api_key=api_key_input)
                        res = client.chat.completions.create(
                            model="gpt-4",
                            messages=[{"role": "user", "content": prompt}]
                        )
                        response = res.choices[0].message.content
                        
                    elif ai_choice == "DeepSeek V3":
                        client = openai.OpenAI(api_key=api_key_input, base_url="https://api.deepseek.com")
                        res = client.chat.completions.create(
                            model="deepseek-chat",
                            messages=[{"role": "user", "content": prompt}]
                        )
                        response = res.choices[0].message.content

                    st.subheader(f"Hasil Analisis {ai_choice}:")
                    st.markdown(response)
                    
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {str(e)}")