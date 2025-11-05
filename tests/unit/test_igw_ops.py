"""Unit tests for Internet Gateway operations."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from vpc_reporter.aws.client import AWSClient
from vpc_reporter.operations.igw_ops import InternetGatewayOperations


@pytest.fixture
def mock_aws_client() -> AWSClient:
    """Create a mock AWS client."""
    client = MagicMock(spec=AWSClient)
    client.region = "us-east-1"
    return client


@pytest.fixture
def igw_ops(mock_aws_client: AWSClient) -> InternetGatewayOperations:
    """Create Internet Gateway operations instance."""
    return InternetGatewayOperations(mock_aws_client)


class TestInternetGatewayOperations:
    """Test Internet Gateway operations class."""

    def test_get_internet_gateways_success(
        self, igw_ops: InternetGatewayOperations, mock_aws_client: AWSClient
    ) -> None:
        """Test successful internet gateway retrieval."""
        mock_aws_client.describe_internet_gateways.return_value = {
            "InternetGateways": [
                {
                    "InternetGatewayId": "igw-123",
                    "Attachments": [
                        {
                            "VpcId": "vpc-123",
                            "State": "available",
                        }
                    ],
                    "Tags": [{"Key": "Name", "Value": "Main IGW"}],
                }
            ]
        }

        result = igw_ops.get_internet_gateways("vpc-123")

        assert result["total_count"] == 1
        assert len(result["internet_gateways"]) == 1
        assert result["internet_gateways"][0]["internet_gateway_id"] == "igw-123"
        assert result["internet_gateways"][0]["name"] == "Main IGW"
        # Check attachments instead of state
        assert len(result["internet_gateways"][0]["attachments"]) == 1

    def test_get_internet_gateways_empty(
        self, igw_ops: InternetGatewayOperations, mock_aws_client: AWSClient
    ) -> None:
        """Test VPC with no internet gateways."""
        mock_aws_client.describe_internet_gateways.return_value = {
            "InternetGateways": []
        }

        result = igw_ops.get_internet_gateways("vpc-123")

        assert result["total_count"] == 0
        assert result["internet_gateways"] == []

    def test_get_internet_gateways_detached(
        self, igw_ops: InternetGatewayOperations, mock_aws_client: AWSClient
    ) -> None:
        """Test detached internet gateway."""
        mock_aws_client.describe_internet_gateways.return_value = {
            "InternetGateways": [
                {
                    "InternetGatewayId": "igw-detached",
                    "Attachments": [],
                }
            ]
        }

        result = igw_ops.get_internet_gateways("vpc-123")

        # Detached IGWs are still returned, just with empty attachments
        assert result["total_count"] == 1
        assert len(result["internet_gateways"][0]["attachments"]) == 0
