import io
import os

import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Google Drive API scope
SCOPES = [
    'https://www.googleapis.com/auth/drive.metadata.readonly',
    'https://www.googleapis.com/auth/drive.readonly',
]


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
    # st.write("Please visit this URL to authorize this application:")
    # st.write(auth_url)

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
