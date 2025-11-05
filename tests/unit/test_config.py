"""Unit tests for Configuration management."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import mock_open, patch

from vpc_reporter.config.config import (
    AWSConfig,
    CacheConfig,
    ConfigManager,
    OutputConfig,
    VPCReporterConfig,
)


class TestConfigModels:
    """Test configuration models."""

    def test_aws_config_defaults(self) -> None:
        """Test AWS config default values."""
        config = AWSConfig()

        assert config.profile == "default"
        assert config.default_region == "us-east-1"
        assert config.regions == ["us-east-1"]

    def test_output_config_defaults(self) -> None:
        """Test output config default values."""
        config = OutputConfig()

        assert config.format == "markdown"
        assert config.directory == "./reports"

    def test_cache_config_defaults(self) -> None:
        """Test cache config default values."""
        config = CacheConfig()

        assert config.enabled is True
        assert config.ttl == 300
        assert config.directory == "./.vpc-reporter-cache"

    def test_vpc_reporter_config_defaults(self) -> None:
        """Test main config default values."""
        config = VPCReporterConfig()

        assert isinstance(config.aws, AWSConfig)
        assert isinstance(config.output, OutputConfig)
        assert isinstance(config.cache, CacheConfig)


class TestConfigManager:
    """Test configuration manager."""

    def test_load_config_with_defaults(self) -> None:
        """Test loading config with no file (uses defaults)."""
        with patch.object(Path, "exists", return_value=False):
            manager = ConfigManager()

            assert manager.config.aws.profile == "default"
            assert manager.config.aws.default_region == "us-east-1"

    def test_get_aws_profile(self) -> None:
        """Test getting AWS profile."""
        with patch.object(Path, "exists", return_value=False):
            manager = ConfigManager()

            assert manager.get_aws_profile() == "default"

    def test_get_default_region(self) -> None:
        """Test getting default region."""
        with patch.object(Path, "exists", return_value=False):
            manager = ConfigManager()

            assert manager.get_default_region() == "us-east-1"

    def test_get_regions(self) -> None:
        """Test getting available regions."""
        with patch.object(Path, "exists", return_value=False):
            manager = ConfigManager()

            assert manager.get_regions() == ["us-east-1"]

    def test_is_cache_enabled(self) -> None:
        """Test checking if cache is enabled."""
        with patch.object(Path, "exists", return_value=False):
            manager = ConfigManager()

            assert manager.is_cache_enabled() is True

    def test_get_cache_ttl(self) -> None:
        """Test getting cache TTL."""
        with patch.object(Path, "exists", return_value=False):
            manager = ConfigManager()

            assert manager.get_cache_ttl() == 300

    def test_load_from_yaml_file(self) -> None:
        """Test loading config from YAML file."""
        yaml_content = """
aws:
  profile: test-profile
  default_region: us-west-2
  regions:
    - us-west-2
    - eu-west-1
output:
  format: json
  directory: /tmp/reports
cache:
  enabled: false
  ttl: 600
"""
        with patch("builtins.open", mock_open(read_data=yaml_content)):
            with patch.object(Path, "exists", return_value=True):
                manager = ConfigManager(Path("/fake/config.yaml"))

                assert manager.config.aws.profile == "test-profile"
                assert manager.config.aws.default_region == "us-west-2"
                assert manager.config.output.format == "json"
                assert manager.config.cache.enabled is False
                assert manager.config.cache.ttl == 600
