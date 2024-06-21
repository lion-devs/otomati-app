# 🖥️ Otomati APP

[![Otomati APP CI/CD](https://github.com/JustinHung0407/otomati-app/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/JustinHung0407/otomati-app/actions/workflows/main.yml)

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

This project was inspired by and includes code from the following repository:

- [Streamlit llm-examples](https://github.com/streamlit/llm-examples) by [Streamlit](https://github.com/streamlit)
  - Description: This project provided examples and utilities for integrating large language models with Streamlit applications.

The code is used under the Apache 2.0 license. For more information, please refer to the LICENSE file in this repository and the original project's repository.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.