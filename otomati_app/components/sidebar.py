import streamlit as st

from otomati_app.config import config


class Sidebar:
    def __init__(self):
        self.initialize_session_state()

    @staticmethod
    def initialize_session_state():
        if 'selected_model' not in st.session_state:
            st.session_state['selected_model'] = config.model
        if 'api_keys' not in st.session_state:
            st.session_state['api_keys'] = {
                "OpenAI": config.openai_api_key,
                "AFS": config.afs_api_key,
                "Ollama": config.ollama_api_key
            }

    @staticmethod
    def render_sidebar():
        with st.sidebar:
            st.title("Settings")

            # Model selection
            selected_model = st.selectbox(
                "Select Model",
                options=config.models,
                index=config.models.index(st.session_state['selected_model']),
                key="selected_model_input"
            )

            # Update selected model in session state
            st.session_state['selected_model'] = selected_model

            # Set API key label based on selected model
            api_key_label = f"{selected_model} API Key"

            # Input API key
            api_key = st.text_input(
                api_key_label,
                value=st.session_state['api_keys'][selected_model],
                key=f"{selected_model}_api_key_input",
                type="password"
            )

            # Update API key in session state
            st.session_state['api_keys'][selected_model] = api_key

            # Display appropriate link based on selected model
            if selected_model == "OpenAI":
                st.markdown("[Get an OpenAI API key](https://platform.openai.com/account/api-keys)")
            elif selected_model == "AFS":
                st.markdown("[Get an AFS API key](https://docs.twcc.ai/docs/user-guides/twcc/afs/afs-cloud)")
            elif selected_model == "Ollama":
                st.markdown("[Get an Ollama API key depending on your scenario]("
                            "https://github.com/ollama/ollama/blob/main/docs/api.md)")

            with st.expander("Other Settings"):
                st.markdown("[View the source code](https://github.com/lion-devs/langchain-demo)")


# Initialize sidebar object
otsidebar = Sidebar()
