import streamlit as st
from dotenv import load_dotenv

from otomati_app.components.sidebar import otsidebar
from otomati_app.services.conversation import user_input
from otomati_app.data.pdf_processing import pdf_read
from otomati_app.data.text_processing import get_chunks
from otomati_app.services.vector_store import vector_store

# Load environment variables from .env file
load_dotenv()

st.set_page_config("Chat PDF")
st.header("RAG based Chat with PDF")

# Render sidebar and get the API key
otsidebar.render_sidebar()
selected_model = st.session_state['selected_model']
api_key = st.session_state['api_keys'][selected_model]

uploaded_files = st.file_uploader(
    "Upload your PDF Files and Click on the Submit & Process Button",
    accept_multiple_files=True
)

if 'processing_done' not in st.session_state:
    st.session_state.processing_done = False

if not uploaded_files:
    st.warning("Please upload PDF files to continue.")
if not api_key:
    st.warning(f"Please add your {selected_model} API key to continue.")

if uploaded_files and api_key:
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
        user_input(question, api_key)
