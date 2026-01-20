from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    default_chat_model: str = "gemini/gemini-2.5-flash"
    system_prompt: str = "You are a helpful assistant. Use the following context to answer the user's question."
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
