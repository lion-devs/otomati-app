import streamlit as st
from dotenv import load_dotenv

from otomati_app.components.sidebar import render_sidebar
from otomati_app.utils.conversation import user_input
from otomati_app.utils.pdf_processing import pdf_read
from otomati_app.utils.text_processing import get_chunks
from otomati_app.utils.vector_store import vector_store

# Load environment variables from .env file
load_dotenv()

st.set_page_config("Chat PDF")
st.header("RAG based Chat with PDF")

openai_api_key = render_sidebar()

uploaded_files = st.file_uploader(
    "Upload your PDF Files and Click on the Submit & Process Button",
    accept_multiple_files=True
)

if 'processing_done' not in st.session_state:
    st.session_state.processing_done = False

if not uploaded_files:
    st.warning("Please upload PDF files to continue.")
if not openai_api_key:
    st.warning("Please add your OpenAI API key to continue.")

if uploaded_files and openai_api_key:
    if st.button("Submit & Process"):
        with st.spinner("Processing..."):
            raw_text = pdf_read(uploaded_files)
            text_chunks = get_chunks(raw_text)
            vector_store(text_chunks)
            st.success("Processing done")
            st.session_state.processing_done = True

if st.session_state.processing_done:
    question = st.text_input(
        "Ask something about the PDFs",
        placeholder="Can you summarize the PDFs?",
    )

    if question:
        user_input(question, openai_api_key)
