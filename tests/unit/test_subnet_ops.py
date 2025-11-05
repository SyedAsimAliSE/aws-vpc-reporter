"""Unit tests for Subnet operations."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from vpc_reporter.aws.client import AWSClient
from vpc_reporter.operations.subnet_ops import SubnetOperations


@pytest.fixture
def mock_aws_client() -> AWSClient:
    """Create a mock AWS client."""
    client = MagicMock(spec=AWSClient)
    client.region = "us-east-1"
    return client


@pytest.fixture
def subnet_ops(mock_aws_client: AWSClient) -> SubnetOperations:
    """Create Subnet operations instance."""
    return SubnetOperations(mock_aws_client)


class TestSubnetOperations:
    """Test Subnet operations class."""

    def test_get_subnets_success(self, subnet_ops: SubnetOperations, mock_aws_client: AWSClient) -> None:
        """Test successful subnet retrieval."""
        mock_aws_client.describe_subnets.return_value = {
            "Subnets": [{
                "SubnetId": "subnet-123",
                "VpcId": "vpc-123",
                "CidrBlock": "10.0.1.0/24",
                "AvailabilityZone": "us-east-1a",
                "AvailableIpAddressCount": 251,
                "State": "available",
                "MapPublicIpOnLaunch": True,
                "Tags": [{"Key": "Name", "Value": "Public Subnet"}],
            }]
        }

        result = subnet_ops.get_subnets("vpc-123")

        assert result["total_count"] == 1
        assert len(result["subnets"]) == 1
        assert result["subnets"][0]["subnet_id"] == "subnet-123"
        assert result["subnets"][0]["cidr_block"] == "10.0.1.0/24"
        assert result["subnets"][0]["availability_zone"] == "us-east-1a"
        assert result["subnets"][0]["name"] == "Public Subnet"

    def test_get_subnets_empty(self, subnet_ops: SubnetOperations, mock_aws_client: AWSClient) -> None:
        """Test VPC with no subnets."""
        mock_aws_client.describe_subnets.return_value = {"Subnets": []}

        result = subnet_ops.get_subnets("vpc-123")

        assert result["total_count"] == 0
        assert result["subnets"] == []

    def test_get_subnets_ipv6(self, subnet_ops: SubnetOperations, mock_aws_client: AWSClient) -> None:
        """Test subnet with IPv6 CIDR."""
        mock_aws_client.describe_subnets.return_value = {
            "Subnets": [{
                "SubnetId": "subnet-123",
                "VpcId": "vpc-123",
                "CidrBlock": "10.0.1.0/24",
                "AvailabilityZone": "us-east-1a",
                "AvailableIpAddressCount": 251,
                "State": "available",
                "Ipv6CidrBlockAssociationSet": [{
                    "Ipv6CidrBlock": "2600:1f13:fe8:5a00::/64",
                    "Ipv6CidrBlockState": {"State": "associated"},
                }],
            }]
        }

        result = subnet_ops.get_subnets("vpc-123")

        assert len(result["subnets"][0]["ipv6_cidr_blocks"]) == 1
        assert result["subnets"][0]["ipv6_cidr_blocks"][0]["ipv6_cidr_block"] == "2600:1f13:fe8:5a00::/64"
        assert result["subnets"][0]["ipv6_cidr_blocks"][0]["state"] == "associated"

    def test_get_subnets_outpost(self, subnet_ops: SubnetOperations, mock_aws_client: AWSClient) -> None:
        """Test subnet on AWS Outpost."""
        mock_aws_client.describe_subnets.return_value = {
            "Subnets": [{
                "SubnetId": "subnet-123",
                "VpcId": "vpc-123",
                "CidrBlock": "10.0.1.0/24",
                "AvailabilityZone": "us-east-1a",
                "AvailableIpAddressCount": 251,
                "State": "available",
                "OutpostArn": "arn:aws:outposts:us-east-1:123456789012:outpost/op-1234567890abcdef0",
            }]
        }

        result = subnet_ops.get_subnets("vpc-123")

        assert result["subnets"][0]["outpost_arn"] is not None
        assert "outpost" in result["subnets"][0]["outpost_arn"]
