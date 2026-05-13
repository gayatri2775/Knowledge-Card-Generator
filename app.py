
import os
import streamlit as st
from google import genai
from PyPDF2 import PdfReader
from docx import Document

st.set_page_config(page_title="AI Knowledge Card Generator", page_icon="🧠", layout="wide")

st.title("🧠 AI Knowledge Card Generator")
st.caption("Upload documents or paste text to generate structured AI-powered knowledge cards.")

def get_api_key():
    try:
        return st.secrets.get("GEMINI_API_KEY", None)
    except Exception:
        return os.getenv("GEMINI_API_KEY")

def generate_ai_text(prompt: str):
    api_key = get_api_key()

    if not api_key:
        st.error("Gemini API key not found.")
        st.stop()

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text

def read_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""

    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"

    return text

def read_docx(uploaded_file):
    doc = Document(uploaded_file)
    return "\n".join([para.text for para in doc.paragraphs])

with st.sidebar:
    st.header("How it Works")
    st.write("1. Upload a document or paste text")
    st.write("2. AI extracts key ideas")
    st.write("3. App generates a structured knowledge card")
    st.write("4. Export summaries for quick review")

uploaded_file = st.file_uploader(
    "Upload a TXT, PDF, or DOCX file",
    type=["txt", "pdf", "docx"]
)

manual_text = st.text_area("Or paste text manually", height=250)

document_text = ""

if uploaded_file:
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".txt"):
        document_text = uploaded_file.read().decode("utf-8")

    elif file_name.endswith(".pdf"):
        document_text = read_pdf(uploaded_file)

    elif file_name.endswith(".docx"):
        document_text = read_docx(uploaded_file)

elif manual_text.strip():
    document_text = manual_text

if document_text:
    with st.expander("Preview Extracted Text"):
        st.write(document_text[:5000])

col1, col2 = st.columns(2)

with col1:
    card_type = st.selectbox(
        "Card Type",
        ["Executive Summary", "Research Brief", "Meeting Notes", "Learning Notes", "Business Insights"]
    )

with col2:
    detail_level = st.selectbox(
        "Detail Level",
        ["Concise", "Balanced", "Detailed"]
    )

if st.button("Generate AI Knowledge Card", type="primary"):

    if not document_text.strip():
        st.warning("Please upload a file or paste text.")
        st.stop()

    prompt = f'''
    You are an AI knowledge management assistant.

    Analyze the content below and generate a structured knowledge card.

    CARD TYPE:
    {card_type}

    DETAIL LEVEL:
    {detail_level}

    Return:
    - Title
    - Executive Summary
    - Key Insights
    - Important Facts
    - FAQs
    - Recommended Actions
    - Tags/Themes
    - One Sentence TLDR

    CONTENT:
    {document_text[:20000]}
    '''

    with st.spinner("Generating knowledge card..."):
        response = generate_ai_text(prompt)

    st.subheader("Generated Knowledge Card")
    st.markdown(response)

    st.download_button(
        "Download Knowledge Card",
        response,
        file_name="knowledge_card.md",
        mime="text/markdown"
    )
