# Sentinel-X Backend Configuration

import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    app_name: str = "Sentinel-X"
    version: str = "1.0.0"
    debug: bool = False

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Database
    database_url: str = "postgresql+asyncpg://sentinel:sentinel123@localhost:5432/sentinel-x"
    redis_url: str = "redis://localhost:6379/0"

    # MQTT
    mqtt_broker: str = "192.168.1.100"
    mqtt_port: int = 1883
    mqtt_user: str = "sentinel"
    mqtt_pass: str = "sentinel123"

    # Security
    secret_key: str = "sentinel-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # mTLS
    mtls_cert_path: Optional[str] = None
    mtls_key_path: Optional[str] = None
    mtls_ca_path: Optional[str] = None

    # External services
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "sentinel"
    minio_secret_key: str = "sentinel123"
    minio_bucket: str = "sentinel-x-media"

    # Rules
    rules_config_path: str = "config/rules.yaml"

    class Config:
        env_file = ".env"
        env_prefix = "SENTINEL_"

settings = Settings()