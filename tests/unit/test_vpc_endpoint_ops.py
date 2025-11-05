"""Unit tests for VPC Endpoint operations."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from vpc_reporter.aws.client import AWSClient
from vpc_reporter.operations.vpc_endpoint_ops import VPCEndpointOperations


@pytest.fixture
def mock_aws_client() -> AWSClient:
    """Create a mock AWS client."""
    client = MagicMock(spec=AWSClient)
    client.region = "us-east-1"
    return client


@pytest.fixture
def vpce_ops(mock_aws_client: AWSClient) -> VPCEndpointOperations:
    """Create VPC Endpoint operations instance."""
    return VPCEndpointOperations(mock_aws_client)


class TestVPCEndpointOperations:
    """Test VPC Endpoint operations class."""

    def test_get_vpc_endpoints_success(
        self, vpce_ops: VPCEndpointOperations, mock_aws_client: AWSClient
    ) -> None:
        """Test successful VPC endpoint retrieval."""
        mock_aws_client.describe_vpc_endpoints.return_value = {
            "VpcEndpoints": [
                {
                    "VpcEndpointId": "vpce-123",
                    "VpcId": "vpc-123",
                    "ServiceName": "com.amazonaws.us-east-1.s3",
                    "State": "available",
                    "VpcEndpointType": "Gateway",
                    "RouteTableIds": ["rtb-123"],
                    "Tags": [{"Key": "Name", "Value": "S3 Endpoint"}],
                }
            ]
        }

        result = vpce_ops.get_vpc_endpoints("vpc-123")

        assert result["total_count"] == 1
        assert len(result["vpc_endpoints"]) == 1
        assert result["vpc_endpoints"][0]["vpc_endpoint_id"] == "vpce-123"
        assert (
            result["vpc_endpoints"][0]["service_name"] == "com.amazonaws.us-east-1.s3"
        )
        assert result["vpc_endpoints"][0]["name"] == "S3 Endpoint"

    def test_get_vpc_endpoints_empty(
        self, vpce_ops: VPCEndpointOperations, mock_aws_client: AWSClient
    ) -> None:
        """Test VPC with no endpoints."""
        mock_aws_client.describe_vpc_endpoints.return_value = {"VpcEndpoints": []}

        result = vpce_ops.get_vpc_endpoints("vpc-123")

        assert result["total_count"] == 0
        assert result["vpc_endpoints"] == []

    def test_get_vpc_endpoints_interface(
        self, vpce_ops: VPCEndpointOperations, mock_aws_client: AWSClient
    ) -> None:
        """Test interface VPC endpoint."""
        mock_aws_client.describe_vpc_endpoints.return_value = {
            "VpcEndpoints": [
                {
                    "VpcEndpointId": "vpce-interface",
                    "VpcId": "vpc-123",
                    "ServiceName": "com.amazonaws.us-east-1.ec2",
                    "State": "available",
                    "VpcEndpointType": "Interface",
                    "SubnetIds": ["subnet-123"],
                    "NetworkInterfaceIds": ["eni-123"],
                }
            ]
        }

        result = vpce_ops.get_vpc_endpoints("vpc-123")

        assert result["vpc_endpoints"][0]["vpc_endpoint_type"] == "Interface"
        assert "subnet-123" in result["vpc_endpoints"][0]["subnet_ids"]
