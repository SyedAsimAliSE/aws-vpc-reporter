"""Unit tests for Route Table operations."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from vpc_reporter.aws.client import AWSClient
from vpc_reporter.operations.route_table_ops import RouteTableOperations


@pytest.fixture
def mock_aws_client() -> AWSClient:
    """Create a mock AWS client."""
    client = MagicMock(spec=AWSClient)
    client.region = "us-east-1"
    return client


@pytest.fixture
def rt_ops(mock_aws_client: AWSClient) -> RouteTableOperations:
    """Create Route Table operations instance."""
    return RouteTableOperations(mock_aws_client)


class TestRouteTableOperations:
    """Test Route Table operations class."""

    def test_get_route_tables_success(
        self, rt_ops: RouteTableOperations, mock_aws_client: AWSClient
    ) -> None:
        """Test successful route table retrieval."""
        mock_aws_client.describe_route_tables.return_value = {
            "RouteTables": [
                {
                    "RouteTableId": "rtb-123",
                    "VpcId": "vpc-123",
                    "Routes": [
                        {
                            "DestinationCidrBlock": "10.0.0.0/16",
                            "GatewayId": "local",
                            "State": "active",
                        },
                        {
                            "DestinationCidrBlock": "0.0.0.0/0",
                            "GatewayId": "igw-123",
                            "State": "active",
                        },
                    ],
                    "Associations": [
                        {
                            "RouteTableAssociationId": "rtbassoc-123",
                            "SubnetId": "subnet-123",
                            "Main": False,
                        }
                    ],
                    "Tags": [{"Key": "Name", "Value": "Public RT"}],
                }
            ]
        }

        result = rt_ops.get_route_tables("vpc-123")

        assert result["total_count"] == 1
        assert len(result["route_tables"]) == 1
        assert result["route_tables"][0]["route_table_id"] == "rtb-123"
        assert result["route_tables"][0]["name"] == "Public RT"
        assert len(result["route_tables"][0]["routes"]) == 2

    def test_get_route_tables_empty(
        self, rt_ops: RouteTableOperations, mock_aws_client: AWSClient
    ) -> None:
        """Test VPC with no route tables."""
        mock_aws_client.describe_route_tables.return_value = {"RouteTables": []}

        result = rt_ops.get_route_tables("vpc-123")

        assert result["total_count"] == 0
        assert result["route_tables"] == []

    def test_get_route_tables_main(
        self, rt_ops: RouteTableOperations, mock_aws_client: AWSClient
    ) -> None:
        """Test main route table identification."""
        mock_aws_client.describe_route_tables.return_value = {
            "RouteTables": [
                {
                    "RouteTableId": "rtb-main",
                    "VpcId": "vpc-123",
                    "Routes": [],
                    "Associations": [
                        {
                            "RouteTableAssociationId": "rtbassoc-main",
                            "Main": True,
                        }
                    ],
                }
            ]
        }

        result = rt_ops.get_route_tables("vpc-123")

        assert result["route_tables"][0]["is_main"] is True
