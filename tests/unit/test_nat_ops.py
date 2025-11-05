"""Unit tests for NAT Gateway operations."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from vpc_reporter.aws.client import AWSClient
from vpc_reporter.operations.nat_ops import NATGatewayOperations


@pytest.fixture
def mock_aws_client() -> AWSClient:
    """Create a mock AWS client."""
    client = MagicMock(spec=AWSClient)
    client.region = "us-east-1"
    return client


@pytest.fixture
def nat_ops(mock_aws_client: AWSClient) -> NATGatewayOperations:
    """Create NAT Gateway operations instance."""
    return NATGatewayOperations(mock_aws_client)


class TestNATGatewayOperations:
    """Test NAT Gateway operations class."""

    def test_get_nat_gateways_success(
        self, nat_ops: NATGatewayOperations, mock_aws_client: AWSClient
    ) -> None:
        """Test successful NAT gateway retrieval."""
        mock_aws_client.describe_nat_gateways.return_value = {
            "NatGateways": [
                {
                    "NatGatewayId": "nat-123",
                    "VpcId": "vpc-123",
                    "SubnetId": "subnet-123",
                    "State": "available",
                    "NatGatewayAddresses": [
                        {
                            "AllocationId": "eipalloc-123",
                            "NetworkInterfaceId": "eni-123",
                            "PrivateIp": "10.0.1.5",
                            "PublicIp": "54.123.45.67",
                        }
                    ],
                    "ConnectivityType": "public",
                    "Tags": [{"Key": "Name", "Value": "NAT GW 1"}],
                }
            ]
        }

        result = nat_ops.get_nat_gateways("vpc-123")

        assert result["total_count"] == 1
        assert len(result["nat_gateways"]) == 1
        assert result["nat_gateways"][0]["nat_gateway_id"] == "nat-123"
        assert result["nat_gateways"][0]["state"] == "available"
        assert result["nat_gateways"][0]["name"] == "NAT GW 1"

    def test_get_nat_gateways_empty(
        self, nat_ops: NATGatewayOperations, mock_aws_client: AWSClient
    ) -> None:
        """Test VPC with no NAT gateways."""
        mock_aws_client.describe_nat_gateways.return_value = {"NatGateways": []}

        result = nat_ops.get_nat_gateways("vpc-123")

        assert result["total_count"] == 0
        assert result["nat_gateways"] == []

    def test_get_nat_gateways_private(
        self, nat_ops: NATGatewayOperations, mock_aws_client: AWSClient
    ) -> None:
        """Test private NAT gateway."""
        mock_aws_client.describe_nat_gateways.return_value = {
            "NatGateways": [
                {
                    "NatGatewayId": "nat-private",
                    "VpcId": "vpc-123",
                    "SubnetId": "subnet-123",
                    "State": "available",
                    "ConnectivityType": "private",
                    "NatGatewayAddresses": [],
                }
            ]
        }

        result = nat_ops.get_nat_gateways("vpc-123")

        assert result["nat_gateways"][0]["connectivity_type"] == "private"
