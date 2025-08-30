from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Load settings from a .env file
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    # API Keys
    GOOGLE_API_KEY: str
    TAVILY_API_KEY: str

    # Model Configuration
    QUERIES_GENERATOR_MODEL: str = "gemini-2.0-flash"
    FACT_CHECKER_MODEL: str = "gemini-2.5-flash"
    POST_WRITER_MODEL: str = "gemini-2.5-flash"

    # Tavily Search Configuration
    TAVILY_SEARCH_DEPTH: str = "advanced"
    TOP_K: int = 5

# Create a single settings instance to be used throughout the application
settings = Settings()