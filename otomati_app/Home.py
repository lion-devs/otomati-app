import streamlit as st
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from otomati_app.components.sidebar import render_sidebar

# Load environment variables from .env file
load_dotenv()

title = "Otomati APP"
st.title(title)

# Render sidebar and get the OpenAI API key
openai_api_key = render_sidebar()


def generate_response(t):
    llm = ChatOpenAI(
        temperature=0,
        model="gpt-3.5-turbo",
        max_retries=3,
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant that tells jokes about {topic}."),
            ("human", "Tell me a joke about {topic}."),
        ]
    )
    chain = prompt | llm
    response = chain.invoke({"topic": t})
    st.info(response.content)


# Form for user input
with st.form("my_form"):
    st.write("This is a simple form to generate a joke about a topic.")
    topic = st.text_area("Enter a topic:", "programming")
    submitted = st.form_submit_button("Submit")
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
    elif submitted:
        generate_response(topic)
