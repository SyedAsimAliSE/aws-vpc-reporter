"""Unit tests for DHCP Options operations."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from vpc_reporter.aws.client import AWSClient
from vpc_reporter.operations.dhcp_ops import DHCPOptionsOperations


@pytest.fixture
def mock_aws_client() -> AWSClient:
    """Create a mock AWS client."""
    client = MagicMock(spec=AWSClient)
    client.region = "us-east-1"
    return client


@pytest.fixture
def dhcp_ops(mock_aws_client: AWSClient) -> DHCPOptionsOperations:
    """Create DHCP Options operations instance."""
    return DHCPOptionsOperations(mock_aws_client)


class TestDHCPOptionsOperations:
    """Test DHCP Options operations class."""

    def test_get_dhcp_options_success(self, dhcp_ops: DHCPOptionsOperations, mock_aws_client: AWSClient) -> None:
        """Test successful DHCP options retrieval."""
        mock_aws_client.describe_dhcp_options.return_value = {
            "DhcpOptions": [{
                "DhcpOptionsId": "dopt-123",
                "DhcpConfigurations": [
                    {
                        "Key": "domain-name",
                        "Values": [{"Value": "example.com"}],
                    },
                    {
                        "Key": "domain-name-servers",
                        "Values": [{"Value": "10.0.0.2"}],
                    },
                ],
                "Tags": [{"Key": "Name", "Value": "Custom DHCP"}],
            }]
        }

        result = dhcp_ops.get_dhcp_options("dopt-123")

        assert result["dhcp_options_id"] == "dopt-123"
        assert result["name"] == "Custom DHCP"
        assert "domain-name" in result["configurations"]
        assert result["configurations"]["domain-name"] == ["example.com"]

    def test_get_dhcp_options_not_found(self, dhcp_ops: DHCPOptionsOperations, mock_aws_client: AWSClient) -> None:
        """Test DHCP options not found."""
        mock_aws_client.describe_dhcp_options.return_value = {"DhcpOptions": []}

        result = dhcp_ops.get_dhcp_options("dopt-nonexistent")

        # When not found, it returns the ID that was searched for
        assert result["dhcp_options_id"] == "dopt-nonexistent"
        assert result["configurations"] == {}

    def test_get_dhcp_options_empty_id(self, dhcp_ops: DHCPOptionsOperations, mock_aws_client: AWSClient) -> None:
        """Test with empty DHCP options ID."""
        result = dhcp_ops.get_dhcp_options("")

        assert result["dhcp_options_id"] is None
        assert result["configurations"] == {}
