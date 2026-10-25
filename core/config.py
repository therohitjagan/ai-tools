from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "Text-to-SQL Assistant with Guardrails"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Storage & DB
    DATABASE_PATH: Path = Field(default_factory=lambda: BASE_DIR / "data" / "enterprise.db")
    READONLY_URI_TEMPLATE: str = "file:{path}?mode=ro"
    
    # Execution & Guardrail thresholds
    MAX_EXECUTION_TIMEOUT_SECONDS: float = 3.0
    MAX_JOIN_DEPTH: int = 6
    MAX_SUBQUERY_DEPTH: int = 4
    DEFAULT_QUERY_LIMIT: int = 100
    MAX_RETURN_ROWS: int = 1000
    STRICT_AST_VALIDATION: bool = True

    # Vector Retrieval & Exemplars
    CHROMA_PERSIST_DIR: Path = Field(default_factory=lambda: BASE_DIR / "data" / "chroma_exemplars")
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EXEMPLAR_TOP_K: int = 3
    SIMILARITY_THRESHOLD: float = 0.35

    # LLM Providers (Optional for cloud LLM inference)
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    LLM_PROVIDER: str = "auto"
    LLM_MODEL: str = "gpt-4o"

    # API Server
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
