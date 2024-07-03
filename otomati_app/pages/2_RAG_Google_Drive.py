import tempfile

import pdfplumber
import streamlit as st
from langchain import hub
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from openai import AuthenticationError

from otomati_app.components.sidebar import otsidebar
from otomati_app.processer.google import download_file_from_google_drive, authenticate_with_google, list_drive_files


def read_pdf(file_content):
    all_text = ""
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(file_content.getbuffer())
        temp_file_path = temp_file.name

    with pdfplumber.open(temp_file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_text += text + "\n"

    return all_text


def read_file(file_content, mime_type):
    if mime_type == 'application/pdf':
        return read_pdf(file_content)
    else:
        return file_content.read().decode('utf-8')


def process_selected_files(file_options, file_dict, files, creds, openai_api_key):
    all_texts = []
    for file_name in file_options:
        file_id = file_dict[file_name]
        mime_type = next(file['mimeType'] for file in files if file['id'] == file_id)
        file_content = download_file_from_google_drive(file_id, mime_type, creds)
        if mime_type == 'application/pdf':
            text = read_pdf(file_content)
        else:
            text = file_content.read().decode('utf-8')
        all_texts.append(text)

    # Create embeddings and index
    embeddings = OpenAIEmbeddings(
        openai_api_key=openai_api_key,
        model="text-embedding-ada-002",
        chunk_size=1000,
        max_retries=3,
        embedding_ctx_length=8191,
    )

    vectorstore = None

    try:
        # Create vectorstore and save the documents
        vectorstore = Chroma.from_texts(all_texts, embeddings)
        st.session_state.documents = all_texts
    except AuthenticationError:
        st.error("Invalid OpenAI API key. Please check and try again.")

    return vectorstore


retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")


def main():
    st.title('Upload from Google Drive')
    st.write('Click the button below to authenticate with Google and list your Google Drive files.')

    # Render sidebar and get the API key
    otsidebar.render_sidebar()
    selected_model = st.session_state['selected_model']
    api_key = st.session_state['api_keys'][selected_model]

    # Check if the user is authenticated
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if not api_key:
        st.warning(f"Please add your {selected_model} API key to continue.")

    # Authenticate with Google Drive
    if st.button('Upload from Google Drive'):
        with st.spinner('Authenticating with Google...'):
            creds = authenticate_with_google()
            st.session_state.creds = creds
            st.session_state.authenticated = True

    # List files in Google Drive
    if st.session_state.authenticated and api_key:
        files = list_drive_files(
            st.session_state.creds,
            pageSize=50,
            fields="nextPageToken, files(id, name, mimeType)",
            orderBy='modifiedByMeTime desc',
            q="mimeType='application/vnd.google-apps.folder' "
              "or mimeType != 'application/vnd.google-apps.folder' "
              "and trashed = false"
        )
        file_dict = {
            f"{file['name']} ({'Folder' if file['mimeType'] == 'application/vnd.google-apps.folder' else 'File'})":
                file['id'] for file in files}
        file_options = st.multiselect('Select files or folders', list(file_dict.keys()))

        if st.button('Retrieve files'):
            vectorstore = process_selected_files(file_options, file_dict, files, st.session_state.creds, api_key)
            if vectorstore:
                st.session_state.vectorstore = vectorstore
                st.success("Files processed successfully.")

    # Form for user query
    if 'vectorstore' in st.session_state and 'documents' in st.session_state:
        query = st.text_input("Enter your query:")
        if query:
            try:
                llm = ChatOpenAI(
                    openai_api_key=api_key,
                    model="gpt-3.5-turbo",
                    max_retries=3,
                )
                retriever = st.session_state.vectorstore.as_retriever()
                combine_docs_chain = create_stuff_documents_chain(llm, retrieval_qa_chat_prompt)
                retrieval_chain = create_retrieval_chain(
                    retriever=retriever,
                    combine_docs_chain=combine_docs_chain
                )
                response = retrieval_chain.invoke({"input": query, "documents": st.session_state.documents})
                st.write(response["answer"])
            except AuthenticationError:
                st.error("Invalid OpenAI API key. Please check and try again.")


if __name__ == '__main__':
    main()
