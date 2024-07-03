# config.py

import os


class Config:
    def __init__(self):
        self.openai_api_key = ""
        self.afs_api_key = ""
        self.ollama_api_key = ""
        self.model = "OpenAI"  # Default model
        self.models = ["OpenAI", "AFS", "Ollama"]

    def load_from_env(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY', self.openai_api_key)
        self.afs_api_key = os.getenv('AFS_API_KEY', self.afs_api_key)
        self.ollama_api_key = os.getenv('OLLAMA_API_KEY', self.ollama_api_key)
        self.model = os.getenv('MODEL', self.model)


config = Config()
config.load_from_env()
