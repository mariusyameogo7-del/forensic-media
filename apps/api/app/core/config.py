import os
from typing import List
from pydantic import BaseModel, Field

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict

    class Settings(BaseSettings):
        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            case_sensitive=True,
            extra="ignore"
        )

        ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
        DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("true", "1")
        PROJECT_NAME: str = "Plateforme africaine de vérification numérique"
        API_V1_STR: str = "/api/v1"
        SECRET_KEY: str = os.getenv("SECRET_KEY", "replace-with-a-secure-random-secret-key-in-production")
        ADMIN_SECRET_KEY: str = os.getenv("ADMIN_SECRET_KEY", "forensic_admin_2026")

        FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
        CORS_ORIGINS: List[str] = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "https://forensic-media.vercel.app",
        ]

        DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgrespassword@localhost:5432/forensic_media")

        SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
        SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "dummy-service-role-key")
        SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "dummy-anon-key")
        SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "dummy-jwt-secret")

        STORAGE_BUCKET_ORIGINALS: str = "media-originals"
        STORAGE_BUCKET_PREVIEWS: str = "media-previews"
        STORAGE_BUCKET_REPORTS: str = "analysis-reports"

        REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
        CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

        HIVE_API_KEY: str = os.getenv("HIVE_API_KEY", "")
        HIVE_API_ENDPOINT: str = "https://api.thehive.ai/api/v2/task/sync"
        GOOGLE_APPLICATION_CREDENTIALS_JSON: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON", "")
        GOOGLE_CLOUD_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT", "forensic-media-dev")
        GOOGLE_FACT_CHECK_API_KEY: str = os.getenv("GOOGLE_FACT_CHECK_API_KEY", "")

        MAX_UPLOAD_SIZE_BYTES: int = 20 * 1024 * 1024  # 20 MiB
        ANONYMOUS_TOKEN_EXPIRY_DAYS: int = 30
        DEFAULT_RETAIN_ORIGINAL_FILES: bool = False
        DEFAULT_RETAIN_ANALYSIS_HISTORY: bool = True

except ImportError:
    class Settings(BaseModel):
        ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
        DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("true", "1")
        PROJECT_NAME: str = "Plateforme africaine de vérification numérique"
        API_V1_STR: str = "/api/v1"
        SECRET_KEY: str = os.getenv("SECRET_KEY", "replace-with-a-secure-random-secret-key-in-production")
        ADMIN_SECRET_KEY: str = os.getenv("ADMIN_SECRET_KEY", "forensic_admin_2026")

        FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
        CORS_ORIGINS: List[str] = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "https://forensic-media.vercel.app",
        ]

        DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgrespassword@localhost:5432/forensic_media")

        SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
        SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "dummy-service-role-key")
        SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "dummy-anon-key")
        SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "dummy-jwt-secret")

        STORAGE_BUCKET_ORIGINALS: str = "media-originals"
        STORAGE_BUCKET_PREVIEWS: str = "media-previews"
        STORAGE_BUCKET_REPORTS: str = "analysis-reports"

        REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
        CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

        HIVE_API_KEY: str = os.getenv("HIVE_API_KEY", "")
        HIVE_API_ENDPOINT: str = "https://api.thehive.ai/api/v2/task/sync"
        GOOGLE_APPLICATION_CREDENTIALS_JSON: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON", "")
        GOOGLE_CLOUD_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT", "forensic-media-dev")
        GOOGLE_FACT_CHECK_API_KEY: str = os.getenv("GOOGLE_FACT_CHECK_API_KEY", "")

        MAX_UPLOAD_SIZE_BYTES: int = 20 * 1024 * 1024  # 20 MiB
        ANONYMOUS_TOKEN_EXPIRY_DAYS: int = 30
        DEFAULT_RETAIN_ORIGINAL_FILES: bool = False
        DEFAULT_RETAIN_ANALYSIS_HISTORY: bool = True


settings = Settings()
