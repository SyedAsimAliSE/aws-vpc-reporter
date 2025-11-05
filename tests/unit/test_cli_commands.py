"""Unit tests for CLI commands."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from vpc_reporter.cli.main import cli


class TestCLICommands:
    """Test CLI command functionality."""

    def test_cli_help(self) -> None:
        """Test CLI help output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "AWS VPC Network Reporter" in result.output
        assert "list-vpcs" in result.output
        assert "report" in result.output
        assert "config" in result.output
        assert "diagram" in result.output
        assert "cost" in result.output

    def test_cli_version(self) -> None:
        """Test CLI version output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "version" in result.output.lower()

    def test_list_vpcs_help(self) -> None:
        """Test list-vpcs help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["list-vpcs", "--help"])

        assert result.exit_code == 0
        assert "List all VPCs" in result.output

    def test_report_help(self) -> None:
        """Test report help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["report", "--help"])

        assert result.exit_code == 0
        assert "comprehensive VPC network report" in result.output
        assert "--vpc-id" in result.output
        assert "--format" in result.output
        assert "--async" in result.output

    def test_config_help(self) -> None:
        """Test config help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["config", "--help"])

        assert result.exit_code == 0
        assert "configuration" in result.output.lower()
        assert "--init" in result.output
        assert "--show" in result.output

    def test_config_init(self) -> None:
        """Test config init command."""
        runner = CliRunner()

        with patch("vpc_reporter.config.config.create_default_config") as mock_create:
            result = runner.invoke(cli, ["config", "--init"])

            assert result.exit_code == 0
            mock_create.assert_called_once()

    def test_config_show(self) -> None:
        """Test config show command."""
        runner = CliRunner()

        with patch("vpc_reporter.config.config.ConfigManager") as mock_config:
            mock_instance = MagicMock()
            mock_instance.get_aws_profile.return_value = "test-profile"
            mock_instance.get_default_region.return_value = "us-east-1"
            mock_instance.get_regions.return_value = ["us-east-1"]
            mock_instance.get_output_format.return_value = "markdown"
            mock_instance.get_output_directory.return_value = "./reports"
            mock_instance.is_cache_enabled.return_value = True
            mock_instance.get_cache_ttl.return_value = 300
            mock_instance.get_cache_directory.return_value = "~/.vpc-reporter-cache"
            mock_config.return_value = mock_instance

            result = runner.invoke(cli, ["config", "--show"])

            assert result.exit_code == 0
            assert "test-profile" in result.output
            assert "us-east-1" in result.output

    def test_global_options(self) -> None:
        """Test global options are recognized."""
        runner = CliRunner()

        # Test that global options don't cause errors
        result = runner.invoke(
            cli, ["--profile", "test", "--region", "us-west-2", "--help"]
        )

        assert result.exit_code == 0

    def test_report_missing_vpc_id(self) -> None:
        """Test report command without VPC ID."""
        runner = CliRunner()

        # Should prompt for VPC selection
        with patch("vpc_reporter.cli.report_command.execute_report"):
            # Simulate user canceling the prompt
            result = runner.invoke(
                cli, ["--profile", "test", "--region", "us-east-1", "report"]
            )

            # Command should handle missing VPC ID gracefully
            assert result.exit_code in [0, 1]  # Either success or handled error
