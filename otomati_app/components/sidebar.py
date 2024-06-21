import streamlit as st


def render_sidebar():
    with st.sidebar:
        st.title("Settings")

        key = st.text_input(
            "OpenAI API Key", key="openai_api_key", type="password"
        )
        st.markdown("[Get an OpenAI API key](https://platform.openai.com/account/api-keys)")

        with st.expander("Other Settings"):
            st.markdown("[View the source code](https://github.com/lion-devs/langchain-demo)")
            # Add more settings here if needed

    return key
