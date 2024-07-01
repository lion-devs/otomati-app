import streamlit as st


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
            st.session_state.openai_api_key = key

        st.markdown("[Get an OpenAI API key](https://platform.openai.com/account/api-keys)")

        with st.expander("Other Settings"):
            st.markdown("[View the source code](https://github.com/lion-devs/langchain-demo)")
            # Add more settings here if needed

    # if not st.session_state.openai_api_key:
    #     st.warning("Please add your OpenAI API key first.")

    return st.session_state['openai_api_key']
