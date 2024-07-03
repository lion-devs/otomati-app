class Settings:
    def __init__(self, model, api_keys):
        self.selected_model = model
        self.api_keys = api_keys

    @classmethod
    def from_config(cls, config):
        api_keys = {
            "OpenAI": config.openai_api_key,
            "AFS": config.afs_api_key,
            "Ollama": config.ollama_api_key
        }
        return cls(config.model, api_keys)
