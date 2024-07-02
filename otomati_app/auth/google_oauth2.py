import base64
import json
import os

import streamlit as st
# Load environment variables from .env file
from dotenv import load_dotenv
from streamlit_oauth import OAuth2Component


# https://github.com/dnplus/streamlit-oauth/tree/main/examples/google.py
def login_google_oauth2():
    load_dotenv()

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    credentials_path = os.path.join(project_root, 'otomati_app', 'credentials.json')

    with open(credentials_path) as f:
        credentials = json.load(f)

    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps

    client_id = credentials['web']['client_id']
    client_secret = credentials['web']['client_secret']
    authorize_endpoint = credentials['web']['auth_uri']
    token_endpoint = credentials['web']['token_uri']
    redirect_uri = credentials['web']['redirect_uris'][0]
    revoke_endpoint = "https://oauth2.googleapis.com/revoke"

    if "auth" not in st.session_state:
        # create a button to start the OAuth2 flow
        oauth2 = OAuth2Component(
            client_id,
            client_secret,
            authorize_endpoint,
            token_endpoint,
            token_endpoint,
            revoke_endpoint
        )

        result = oauth2.authorize_button(
            name="Continue with Google",
            icon="https://www.google.com.tw/favicon.ico",
            redirect_uri=redirect_uri,
            scope="openid email profile",
            key="google",
            extras_params={"prompt": "consent", "access_type": "offline"},
            use_container_width=True,
            pkce='S256',
        )

        if result:
            st.write(result)
            # decode the id_token jwt and get the user's email address
            id_token = result["token"]["id_token"]
            # verify the signature is an optional step for security
            payload = id_token.split(".")[1]
            # add padding to the payload if needed
            payload += "=" * (-len(payload) % 4)
            payload = json.loads(base64.b64decode(payload))
            email = payload["email"]
            st.session_state["auth"] = email
            st.session_state["token"] = result["token"]
            st.session_state["creds"] = result["token"]
            st.session_state["authenticated"] = True
            st.rerun()
    else:
        st.write("You are logged in!")
        st.write(st.session_state["auth"])
        st.write(st.session_state["token"])
        if st.button("Logout"):
            del st.session_state["auth"]
            del st.session_state["token"]
            del st.session_state["creds"]
            st.session_state["authenticated"] = False
            st.rerun()
