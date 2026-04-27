from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # LLM Settings
    LLM_API_KEY: str = "default_key"  # Adding default for tests, in prod this should be env var
    LLM_MODEL_NAME: str = "gpt-4-turbo"
    
    # Memory Settings
    STM_TOKEN_LIMIT: int = 4000
    DECAY_RATE: float = 0.01  # 记忆衰减系数 lambda
    
    # Vector DB Settings
    MILVUS_URI: str = "./milvus.db"
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
