import io

import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Google Drive API scope
SCOPES = [
    'https://www.googleapis.com/auth/drive.metadata.readonly',
    'https://www.googleapis.com/auth/drive.readonly',
]
REDIRECT_URI = 'http://localhost:8501'


def authenticate_with_google():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json',
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

    # Save the state to the session
    st.session_state.state = state

    creds = flow.run_local_server(
        port=8080,
        authorization_prompt_message='Please visit this URL: {url}',
        success_message='The auth flow is complete; you may close this window.',
        open_browser=True
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


def main():
    st.title('Upload from Google Drive')
    st.write('Click the button below to authenticate with Google and list your Google Drive files.')

    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if st.button('Upload from Google Drive'):
        with st.spinner('Authenticating with Google...'):
            creds = authenticate_with_google()
            st.session_state.creds = creds
            st.session_state.authenticated = True

    if st.session_state.authenticated:
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

        if st.button('Download selected file'):
            for file_name in file_options:
                file_id = file_dict[file_name]
                mime_type = next(file['mimeType'] for file in files if file['id'] == file_id)
                file_content = download_file_from_google_drive(file_id, mime_type, st.session_state.creds)
                st.download_button(
                    label=f"Download {file_name}",
                    data=file_content,
                    file_name=file_name,
                    mime='application/octet-stream'
                )


if __name__ == '__main__':
    main()
