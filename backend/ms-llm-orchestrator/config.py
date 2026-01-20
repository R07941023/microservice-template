from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    litellm_host: str = "https://litellm.mydormroom.dpdns.org"
    mcp_host: str ="https://mcp-context-forge.mydormroom.dpdns.org/servers/1a6556c61e9a400ea537e7e73c05a2db/mcp"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_host: str = "localhost"
    postgres_port: str = "5432"
    postgres_name: str = "rag"
    default_chat_model: str = "gemini/gemini-2.5-flash"
    system_prompt: str = "You are a helpful assistant. Use the following context to answer the user's question."
    
    @property
    def postgres_uri(self) -> str:
        return f"postgres://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_name}"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
