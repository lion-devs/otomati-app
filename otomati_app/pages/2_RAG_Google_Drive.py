import io
import os
import tempfile

import pdfplumber
import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from langchain import hub
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from openai import AuthenticationError

from otomati_app.components.sidebar import render_sidebar

# Google Drive API scope
SCOPES = [
    'https://www.googleapis.com/auth/drive.metadata.readonly',
    'https://www.googleapis.com/auth/drive.readonly',
]
REDIRECT_URI = 'http://localhost:8501'


def authenticate_with_google():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    credentials_path = os.path.join(project_root, 'otomati_app', 'credentials.json')
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps
    flow = InstalledAppFlow.from_client_secrets_file(
        credentials_path,
        scopes=SCOPES,
    )

    # Get the authorization URL
    auth_url, state = (
        flow.authorization_url(
            prompt='consent',
            include_granted_scopes='true',
            access_type='offline'
        )
    )

    # Display the authorization URL in Streamlit
    st.write("Please visit this URL to authorize this application:")
    st.write(auth_url)

    # Save the state to the session
    st.session_state.state = state

    creds = flow.run_local_server(
        port=8080,
        authorization_prompt_message='Please visit this URL: {url}',
        success_message='The auth flow is complete; you may close this window.',
        open_browser=True,
    )

    return creds


def list_drive_files(creds, **kwargs):
    # Build the service object for Drive API
    service = build('drive', 'v3', credentials=creds)
    # List files in the user's Google Drive
    results = service.files().list(**kwargs).execute()
    items = results.get('files', [])
    return items


def download_file_from_google_drive(file_id, mime_type, creds):
    service = build('drive', 'v3', credentials=creds)
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()

    if 'application/vnd.google-apps' in mime_type:
        # Use export for Google Docs files
        request = service.files().export_media(fileId=file_id, mimeType='application/pdf')
    else:
        # Use get_media for other files
        request = service.files().get_media(fileId=file_id)

    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    fh.seek(0)
    return fh


# def read_pdf(file_content):
#     all_text = ""
#     with pdfplumber.open(file_content) as pdf:
#         for page in pdf.pages:
#             text = page.extract_text()
#             if text:
#                 all_text += text + "\n"
#     return all_text


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

    openai_api_key = render_sidebar()

    # Check if the user is authenticated
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if not openai_api_key:
        st.warning("Please add your OpenAI API key to continue.")

    # Authenticate with Google Drive
    if st.button('Upload from Google Drive'):
        with st.spinner('Authenticating with Google...'):
            creds = authenticate_with_google()
            st.session_state.creds = creds
            st.session_state.authenticated = True

    # List files in Google Drive
    if st.session_state.authenticated and openai_api_key:
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
            vectorstore = process_selected_files(file_options, file_dict, files, st.session_state.creds, openai_api_key)
            if vectorstore:
                st.session_state.vectorstore = vectorstore
                st.success("Files processed successfully.")

    # Form for user query
    if 'vectorstore' in st.session_state and 'documents' in st.session_state:
        query = st.text_input("Enter your query:")
        if query:
            try:
                llm = ChatOpenAI(
                    openai_api_key=openai_api_key,
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
