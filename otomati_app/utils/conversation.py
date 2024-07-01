import streamlit as st
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools.retriever import create_retriever_tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from otomati_app.utils.vector_store import load_vector_store


def get_conversational_chain(tools, ques, key):
    llm = ChatOpenAI(
        openai_api_key=key,
        model_name="gpt-3.5-turbo",
        temperature=0,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a helpful assistant. Answer the question as detailed as possible from the provided context, make sure to provide all the details. If the answer is not in
                provided context just say, "answer is not available in the context", don't provide the wrong answer""",
            ),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )
    tool = [tools]
    agent = create_tool_calling_agent(llm, tool, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tool, verbose=True)
    response = agent_executor.invoke({"input": ques})
    print(response)
    st.write("Reply: ", response['output'])


def user_input(user_question, key):
    new_db = load_vector_store()
    retriever = new_db.as_retriever()
    retrieval_chain = create_retriever_tool(
        retriever,
        "pdf_extractor",
        "This tool is to give answers to queries from the PDF"
    )
    get_conversational_chain(retrieval_chain, user_question, key)
