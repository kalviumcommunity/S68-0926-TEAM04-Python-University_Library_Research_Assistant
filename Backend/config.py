import os


def _load_env_file(path: str = ".env") -> None:
    """Load environment values without requiring the optional settings package."""
    if not os.path.isfile(path):
        return

    with open(path, encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


_load_env_file()


class Settings:
    app_name: str = os.getenv("APP_NAME", "University Library Research Assistant")
    environment: str = os.getenv("ENVIRONMENT", "development")
    llm_provider: str = os.getenv("LLM_PROVIDER", "")
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "")


settings = Settings()
