"""Unit tests for VPC Peering operations."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from vpc_reporter.aws.client import AWSClient
from vpc_reporter.operations.peering_ops import VPCPeeringOperations


@pytest.fixture
def mock_aws_client() -> AWSClient:
    """Create a mock AWS client."""
    client = MagicMock(spec=AWSClient)
    client.region = "us-east-1"
    return client


@pytest.fixture
def peering_ops(mock_aws_client: AWSClient) -> VPCPeeringOperations:
    """Create VPC Peering operations instance."""
    return VPCPeeringOperations(mock_aws_client)


class TestVPCPeeringOperations:
    """Test VPC Peering operations class."""

    def test_get_vpc_peering_connections_success(self, peering_ops: VPCPeeringOperations, mock_aws_client: AWSClient) -> None:
        """Test successful VPC peering retrieval."""
        mock_aws_client.describe_vpc_peering_connections.return_value = {
            "VpcPeeringConnections": [{
                "VpcPeeringConnectionId": "pcx-123",
                "Status": {"Code": "active"},
                "RequesterVpcInfo": {
                    "VpcId": "vpc-123",
                    "CidrBlock": "10.0.0.0/16",
                    "Region": "us-east-1",
                },
                "AccepterVpcInfo": {
                    "VpcId": "vpc-456",
                    "CidrBlock": "10.1.0.0/16",
                    "Region": "us-west-2",
                },
                "Tags": [{"Key": "Name", "Value": "Prod-Dev Peering"}],
            }]
        }

        result = peering_ops.get_vpc_peering_connections("vpc-123")

        assert result["total_count"] == 1
        assert len(result["peering_connections"]) == 1
        assert result["peering_connections"][0]["vpc_peering_connection_id"] == "pcx-123"
        assert result["peering_connections"][0]["status_code"] == "active"
        assert result["peering_connections"][0]["name"] == "Prod-Dev Peering"

    def test_get_vpc_peering_connections_empty(self, peering_ops: VPCPeeringOperations, mock_aws_client: AWSClient) -> None:
        """Test VPC with no peering connections."""
        mock_aws_client.describe_vpc_peering_connections.return_value = {"VpcPeeringConnections": []}

        result = peering_ops.get_vpc_peering_connections("vpc-123")

        assert result["total_count"] == 0
        assert result["peering_connections"] == []

    def test_get_vpc_peering_connections_pending(self, peering_ops: VPCPeeringOperations, mock_aws_client: AWSClient) -> None:
        """Test pending VPC peering connection."""
        mock_aws_client.describe_vpc_peering_connections.return_value = {
            "VpcPeeringConnections": [{
                "VpcPeeringConnectionId": "pcx-pending",
                "Status": {"Code": "pending-acceptance"},
                "RequesterVpcInfo": {"VpcId": "vpc-123", "CidrBlock": "10.0.0.0/16"},
                "AccepterVpcInfo": {"VpcId": "vpc-456", "CidrBlock": "10.1.0.0/16"},
            }]
        }

        result = peering_ops.get_vpc_peering_connections("vpc-123")

        assert result["peering_connections"][0]["status_code"] == "pending-acceptance"
