"""Unit tests for Elastic IP operations."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from vpc_reporter.aws.client import AWSClient
from vpc_reporter.operations.eip_ops import ElasticIPOperations


@pytest.fixture
def mock_aws_client() -> AWSClient:
    """Create a mock AWS client."""
    client = MagicMock(spec=AWSClient)
    client.region = "us-east-1"
    return client


@pytest.fixture
def eip_ops(mock_aws_client: AWSClient) -> ElasticIPOperations:
    """Create Elastic IP operations instance."""
    return ElasticIPOperations(mock_aws_client)


class TestElasticIPOperations:
    """Test Elastic IP operations class."""

    def test_get_elastic_ips_success(
        self, eip_ops: ElasticIPOperations, mock_aws_client: AWSClient
    ) -> None:
        """Test successful Elastic IP retrieval."""
        mock_aws_client.describe_addresses.return_value = {
            "Addresses": [
                {
                    "AllocationId": "eipalloc-123",
                    "PublicIp": "54.123.45.67",
                    "Domain": "vpc",
                    "NetworkInterfaceId": "eni-123",
                    "PrivateIpAddress": "10.0.1.5",
                    "AssociationId": "eipassoc-123",
                    "Tags": [{"Key": "Name", "Value": "NAT EIP"}],
                }
            ]
        }

        result = eip_ops.get_elastic_ips("vpc-123")

        assert result["total_count"] == 1
        assert len(result["elastic_ips"]) == 1
        assert result["elastic_ips"][0]["allocation_id"] == "eipalloc-123"
        assert result["elastic_ips"][0]["public_ip"] == "54.123.45.67"
        assert result["elastic_ips"][0]["name"] == "NAT EIP"

    def test_get_elastic_ips_empty(
        self, eip_ops: ElasticIPOperations, mock_aws_client: AWSClient
    ) -> None:
        """Test VPC with no Elastic IPs."""
        mock_aws_client.describe_addresses.return_value = {"Addresses": []}

        result = eip_ops.get_elastic_ips("vpc-123")

        assert result["total_count"] == 0
        assert result["elastic_ips"] == []

    def test_get_elastic_ips_unassociated(
        self, eip_ops: ElasticIPOperations, mock_aws_client: AWSClient
    ) -> None:
        """Test unassociated Elastic IP."""
        mock_aws_client.describe_addresses.return_value = {
            "Addresses": [
                {
                    "AllocationId": "eipalloc-unassoc",
                    "PublicIp": "54.123.45.68",
                    "Domain": "vpc",
                }
            ]
        }

        result = eip_ops.get_elastic_ips("vpc-123")

        assert result["elastic_ips"][0]["network_interface_id"] is None
        assert result["elastic_ips"][0]["association_id"] is None
