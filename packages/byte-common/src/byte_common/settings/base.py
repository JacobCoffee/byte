"""Base settings for all Byte services."""

from __future__ import annotations

import binascii
import os

from pydantic import field_validator
from pydantic.types import SecretBytes
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ("BaseAppSettings",)


class BaseAppSettings(BaseSettings):
    """Base settings for all Byte services.

    All services (bot, API, worker) should inherit from this class
    to ensure consistent configuration patterns.
    """

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ENVIRONMENT: str = "prod"
    """Application environment (dev, test, prod)."""
    DEBUG: bool = False
    """Enable debug mode."""
    SECRET_KEY: SecretBytes
    """Secret key used for signing and encryption."""

    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def generate_secret_key(cls, value: str | None) -> SecretBytes:
        """Generate a secret key if not provided.

        Args:
            value: A secret key, or None to generate one.

        Returns:
            A secret key as SecretBytes.
        """
        if value is None:
            return SecretBytes(binascii.hexlify(os.urandom(32)))
        return SecretBytes(value.encode())
