# config.py

class Config:
    def __init__(self):
        self.openai_api_key = ""
        self.model = "OpenAI"  # Default model
        self.models = ["OpenAI", "AFS", "Ollama"]

    def load_from_env(self):
        import os
        self.openai_api_key = os.getenv('OPENAI_API_KEY', self.openai_api_key)
        self.model = os.getenv('MODEL', self.model)


config = Config()
config.load_from_env()
