"""Unit tests for VPC operations."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError

from vpc_reporter.aws.client import AWSClient
from vpc_reporter.operations.vpc_ops import VPCOperations


@pytest.fixture
def mock_aws_client() -> AWSClient:
    """Create a mock AWS client."""
    client = MagicMock(spec=AWSClient)
    client.region = "us-east-1"
    client.profile = "test"
    return client


@pytest.fixture
def vpc_ops(mock_aws_client: AWSClient) -> VPCOperations:
    """Create VPC operations instance."""
    return VPCOperations(mock_aws_client)


class TestVPCOperations:
    """Test VPC operations class."""

    def test_list_vpcs_success(
        self, vpc_ops: VPCOperations, mock_aws_client: AWSClient
    ) -> None:
        """Test successful VPC listing."""
        mock_aws_client.describe_vpcs.return_value = {
            "Vpcs": [
                {
                    "VpcId": "vpc-123",
                    "CidrBlock": "10.0.0.0/16",
                    "State": "available",
                    "Tags": [{"Key": "Name", "Value": "Test VPC"}],
                }
            ]
        }

        vpcs = vpc_ops.list_vpcs()

        assert len(vpcs) == 1
        assert vpcs[0]["vpc_id"] == "vpc-123"
        assert vpcs[0]["cidr_block"] == "10.0.0.0/16"
        assert vpcs[0]["name"] == "Test VPC"

    def test_list_vpcs_empty(
        self, vpc_ops: VPCOperations, mock_aws_client: AWSClient
    ) -> None:
        """Test listing VPCs when none exist."""
        mock_aws_client.describe_vpcs.return_value = {"Vpcs": []}

        vpcs = vpc_ops.list_vpcs()

        assert vpcs == []

    def test_get_vpc_details_success(
        self, vpc_ops: VPCOperations, mock_aws_client: AWSClient
    ) -> None:
        """Test getting VPC details."""
        mock_aws_client.describe_vpcs.return_value = {
            "Vpcs": [
                {
                    "VpcId": "vpc-123",
                    "CidrBlock": "10.0.0.0/16",
                    "State": "available",
                    "DhcpOptionsId": "dopt-123",
                    "InstanceTenancy": "default",
                    "IsDefault": False,
                    "Tags": [{"Key": "Name", "Value": "Test VPC"}],
                }
            ]
        }

        vpc = vpc_ops.get_vpc_details("vpc-123")

        assert vpc["vpc_id"] == "vpc-123"
        assert vpc["cidr_block"] == "10.0.0.0/16"
        assert vpc["dhcp_options_id"] == "dopt-123"
        assert vpc["name"] == "Test VPC"

    def test_get_vpc_details_not_found(
        self, vpc_ops: VPCOperations, mock_aws_client: AWSClient
    ) -> None:
        """Test getting details for non-existent VPC."""
        mock_aws_client.describe_vpcs.side_effect = ClientError(
            {"Error": {"Code": "InvalidVpcID.NotFound", "Message": "VPC not found"}},
            "DescribeVpcs",
        )

        with pytest.raises(ClientError):
            vpc_ops.get_vpc_details("vpc-nonexistent")

    def test_get_vpc_details_no_name_tag(
        self, vpc_ops: VPCOperations, mock_aws_client: AWSClient
    ) -> None:
        """Test VPC without Name tag."""
        mock_aws_client.describe_vpcs.return_value = {
            "Vpcs": [
                {
                    "VpcId": "vpc-123",
                    "CidrBlock": "10.0.0.0/16",
                    "State": "available",
                    "Tags": [],
                }
            ]
        }

        vpc = vpc_ops.get_vpc_details("vpc-123")

        assert vpc["name"] is None

    def test_get_vpc_details_multiple_cidrs(
        self, vpc_ops: VPCOperations, mock_aws_client: AWSClient
    ) -> None:
        """Test VPC with multiple CIDR blocks."""
        mock_aws_client.describe_vpcs.return_value = {
            "Vpcs": [
                {
                    "VpcId": "vpc-123",
                    "CidrBlock": "10.0.0.0/16",
                    "State": "available",
                    "CidrBlockAssociationSet": [
                        {
                            "CidrBlock": "10.0.0.0/16",
                            "CidrBlockState": {"State": "associated"},
                        },
                        {
                            "CidrBlock": "10.1.0.0/16",
                            "CidrBlockState": {"State": "associated"},
                        },
                    ],
                }
            ]
        }

        vpc = vpc_ops.get_vpc_details("vpc-123")

        # Check that raw_data contains the CIDR associations
        assert "CidrBlockAssociationSet" in vpc["raw_data"]
        assert len(vpc["raw_data"]["CidrBlockAssociationSet"]) == 2

    def test_get_tag_value_helper(self, vpc_ops: VPCOperations) -> None:
        """Test tag extraction helper method."""
        tags = [
            {"Key": "Name", "Value": "MyVPC"},
            {"Key": "Environment", "Value": "prod"},
        ]

        assert vpc_ops._get_tag_value(tags, "Name") == "MyVPC"
        assert vpc_ops._get_tag_value(tags, "Environment") == "prod"
        assert vpc_ops._get_tag_value(tags, "NonExistent") is None
        assert vpc_ops._get_tag_value([], "Name") is None
