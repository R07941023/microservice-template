from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ollama_endpoint: str = "http://host.docker.internal:11434"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_host: str = "localhost"
    postgres_port: str = "5432"
    postgres_name: str = "rag"
    
    default_chat_model: str = "gpt-oss:20b"
    embedding_model: str = "nomic-embed-text"
    
    maplestory_user_name: str = "maplestory"

    @property
    def postgres_uri(self) -> str:
        return f"postgres://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_name}"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
