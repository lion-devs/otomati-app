import streamlit as st

from otomati_app.config.config import config


def render_sidebar():
    with st.sidebar:
        st.title("Settings")

        # Store the OpenAI API key in the session state
        if 'openai_api_key' not in st.session_state:
            st.session_state['openai_api_key'] = ''

        key = st.text_input(
            "OpenAI API Key",
            value=st.session_state['openai_api_key'],
            key="input_openai_api_key",
            type="password"
        )

        if key:
            st.session_state['openai_api_key'] = key

        st.markdown("[Get an OpenAI API key](https://platform.openai.com/account/api-keys)")

        st.selectbox(
            "Select Model",
            options=config.models,
            index=config.models.index(config.model),
            key="selected_model"
        )

        if 'selected_model' not in st.session_state:
            st.session_state['selected_model'] = config.model

        with st.expander("Other Settings"):
            st.markdown("[View the source code](https://github.com/lion-devs/langchain-demo)")

    return st.session_state['openai_api_key']
