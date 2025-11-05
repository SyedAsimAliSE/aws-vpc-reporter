"""Configuration file support for vpc-reporter."""

from __future__ import annotations

from pathlib import Path

import yaml
from loguru import logger
from pydantic import BaseModel, Field


class AWSConfig(BaseModel):
    """AWS configuration."""

    profile: str = Field(default="default", description="AWS profile name")
    default_region: str = Field(default="us-east-1", description="Default AWS region")
    regions: list[str] = Field(default_factory=lambda: ["us-east-1"], description="Available regions")


class OutputConfig(BaseModel):
    """Output configuration."""

    format: str = Field(default="markdown", description="Default output format")
    directory: str = Field(default="./reports", description="Output directory")


class CacheConfig(BaseModel):
    """Cache configuration."""

    enabled: bool = Field(default=True, description="Enable caching")
    ttl: int = Field(default=300, description="Cache TTL in seconds")
    directory: str = Field(default="./.vpc-reporter-cache", description="Cache directory")


class VPCReporterConfig(BaseModel):
    """Main configuration model."""

    aws: AWSConfig = Field(default_factory=AWSConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)


class ConfigManager:
    """Configuration file manager."""

    DEFAULT_CONFIG_PATHS = [
        Path.cwd() / ".vpc-reporter" / "config.yaml",
        Path.cwd() / ".vpc-reporter" / "config.yml",
        Path.cwd() / ".vpc-reporter.yaml",
        Path.cwd() / ".vpc-reporter.yml",
    ]

    def __init__(self, config_path: str | Path | None = None) -> None:
        """Initialize configuration manager.

        Args:
            config_path: Optional path to config file
        """
        self.config_path = Path(config_path) if config_path else None
        self.config = self._load_config()

    def _load_config(self) -> VPCReporterConfig:
        """Load configuration from file or use defaults.

        Returns:
            Configuration object
        """
        # Try explicit path first
        if self.config_path and self.config_path.exists():
            return self._load_from_file(self.config_path)

        # Try default paths
        for path in self.DEFAULT_CONFIG_PATHS:
            if path.exists():
                logger.info(f"Loading config from {path}")
                return self._load_from_file(path)

        # No config file found, use defaults
        logger.debug("No config file found, using defaults")
        return VPCReporterConfig()

    def _load_from_file(self, path: Path) -> VPCReporterConfig:
        """Load configuration from YAML file.

        Args:
            path: Path to config file

        Returns:
            Configuration object
        """
        try:
            with open(path) as f:
                data = yaml.safe_load(f) or {}

            config = VPCReporterConfig(**data)
            logger.info(f"Loaded configuration from {path}")
            return config
        except Exception as e:
            logger.warning(f"Failed to load config from {path}: {e}")
            logger.warning("Using default configuration")
            return VPCReporterConfig()

    def save_config(self, path: str | Path | None = None) -> None:
        """Save current configuration to file.

        Args:
            path: Optional path to save to (defaults to first default path)
        """
        save_path = Path(path) if path else self.DEFAULT_CONFIG_PATHS[0]
        save_path.parent.mkdir(parents=True, exist_ok=True)

        with open(save_path, "w") as f:
            yaml.dump(self.config.model_dump(), f, default_flow_style=False)

        logger.info(f"Saved configuration to {save_path}")

    def get_aws_profile(self) -> str:
        """Get AWS profile from config."""
        return self.config.aws.profile

    def get_default_region(self) -> str:
        """Get default region from config."""
        return self.config.aws.default_region

    def get_regions(self) -> list[str]:
        """Get available regions from config."""
        return self.config.aws.regions

    def get_output_format(self) -> str:
        """Get default output format from config."""
        return self.config.output.format

    def get_output_directory(self) -> str:
        """Get output directory from config."""
        return self.config.output.directory

    def is_cache_enabled(self) -> bool:
        """Check if caching is enabled."""
        return self.config.cache.enabled

    def get_cache_ttl(self) -> int:
        """Get cache TTL."""
        return self.config.cache.ttl

    def get_cache_directory(self) -> str:
        """Get cache directory."""
        return self.config.cache.directory


def create_default_config(path: str | Path | None = None) -> None:
    """Create a default configuration file.

    Args:
        path: Optional path to create config at
    """
    config_path = Path(path) if path else ConfigManager.DEFAULT_CONFIG_PATHS[0]
    config_path.parent.mkdir(parents=True, exist_ok=True)

    default_config = VPCReporterConfig()

    with open(config_path, "w") as f:
        yaml.dump(default_config.model_dump(), f, default_flow_style=False)

    logger.info(f"Created default configuration at {config_path}")
    print(f"✓ Created default configuration at {config_path}")
    print("\nEdit this file to customize your settings:")
    print(f"  {config_path}")
