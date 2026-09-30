from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    app_name: str = "FIRE-Vision"
    database_url: str = f"sqlite:///{BASE_DIR / 'firevision.db'}"
    evidence_root: Path = BASE_DIR.parent / "evidence_store"
    report_root: Path = BASE_DIR.parent / "reports"
    max_upload_mb: int = 1024
    allowed_extensions: str = ".mp4,.avi,.dav,.264,.265,.bin,.dd,.img,.e01,.mkv,.mov,.ts,.m4v"
    model_path: str = ""
    model_version: str = "optional-yolo"
    api_key: str = ""
    model_config = SettingsConfigDict(env_file=BASE_DIR.parent / ".env", extra="ignore")

settings=Settings()
settings.evidence_root.mkdir(parents=True,exist_ok=True)
settings.report_root.mkdir(parents=True,exist_ok=True)
