# 🖥️ Otomati APP

Otomati APP help communicate with AI models in a more human-like way.

## Overview of the App

This app collects the basic functionalities of the LangChain framework.

Current examples include:

- Chatbot
- File Q&A
- Chat with Internet search
- LangChain Quickstart
- LangChain PromptTemplate
- Chat with user feedback


### Get an OpenAI API key

You can get your own OpenAI API key by following the following instructions:

1. Go to https://platform.openai.com/api-keys.
2. Click on the `+ Create new secret key` button.
3. Next, enter an identifier name (optional) and click on the `Create secret key` button.


## Run it locally

```sh
poetry install
streamlit run otomati_app/Home.py
poetry publish
```

## Acknowledgements

This project is based on [streamlit/llm-examples](https://github.com/streamlit/llm-examples) by Streamlit.