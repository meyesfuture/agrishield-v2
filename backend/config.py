"""
Configuration module for Punjab GrainWatch Backend.
Provides typed configuration, safe path handling, and environment validation.
"""

from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings validated via Pydantic."""
    
    # Project Identity
    PROJECT_NAME: str = "Punjab GrainWatch API"
    VERSION: str = "0.2.0"
    API_V1_STR: str = "/api/v1"
    
    # Server Binding
    API_HOST: str = Field(default="127.0.0.1", description="Host address for FastAPI server")
    API_PORT: int = Field(default=8000, description="Port for FastAPI server")
    
    # CORS Configuration
    FRONTEND_ORIGIN: str = Field(
        default="http://localhost:4321",
        description="Allowed frontend origin for CORS"
    )
    ADDITIONAL_ALLOWED_ORIGINS: List[str] = [
        "http://127.0.0.1:4321",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    
    # Directory Anchors
    WORKSPACE_ROOT: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent
    )
    
    # Environment file configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def data_dir(self) -> Path:
        return self.WORKSPACE_ROOT / "data"

    @property
    def manifests_dir(self) -> Path:
        return self.data_dir / "manifests"

    @property
    def derived_dir(self) -> Path:
        return self.data_dir / "derived"

    @property
    def catalog_json(self) -> Path:
        return self.manifests_dir / "dataset_catalog.json"

    @property
    def catalog_csv(self) -> Path:
        return self.manifests_dir / "dataset_catalog.csv"

    @property
    def quality_report_json(self) -> Path:
        return self.derived_dir / "quality_report.json"

    def resolve_safe_path(self, relative_path: str) -> Optional[Path]:
        """
        Safely resolve a path, ensuring it stays strictly inside WORKSPACE_ROOT.
        Returns None if path traversal is detected.
        """
        try:
            target = (self.WORKSPACE_ROOT / relative_path).resolve()
            # Ensure target is within WORKSPACE_ROOT
            if self.WORKSPACE_ROOT.resolve() in target.parents or target == self.WORKSPACE_ROOT.resolve():
                return target
            return None
        except Exception:
            return None

    @property
    def all_allowed_origins(self) -> List[str]:
        origins = [self.FRONTEND_ORIGIN]
        for org in self.ADDITIONAL_ALLOWED_ORIGINS:
            if org not in origins:
                origins.append(org)
        return origins


# Global cached settings instance
settings = Settings()
