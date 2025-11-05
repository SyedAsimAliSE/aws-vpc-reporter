"""Unit tests for Security Group operations."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from vpc_reporter.aws.client import AWSClient
from vpc_reporter.operations.security_group_ops import SecurityGroupOperations


@pytest.fixture
def mock_aws_client() -> AWSClient:
    """Create a mock AWS client."""
    client = MagicMock(spec=AWSClient)
    client.region = "us-east-1"
    return client


@pytest.fixture
def sg_ops(mock_aws_client: AWSClient) -> SecurityGroupOperations:
    """Create Security Group operations instance."""
    return SecurityGroupOperations(mock_aws_client)


class TestSecurityGroupOperations:
    """Test Security Group operations class."""

    def test_get_security_groups_success(self, sg_ops: SecurityGroupOperations, mock_aws_client: AWSClient) -> None:
        """Test successful security group retrieval."""
        mock_aws_client.describe_security_groups.return_value = {
            "SecurityGroups": [{
                "GroupId": "sg-123",
                "GroupName": "web-sg",
                "Description": "Web server security group",
                "VpcId": "vpc-123",
                "IpPermissions": [{
                    "IpProtocol": "tcp",
                    "FromPort": 80,
                    "ToPort": 80,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                }],
                "IpPermissionsEgress": [{
                    "IpProtocol": "-1",
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                }],
                "Tags": [{"Key": "Name", "Value": "Web SG"}],
            }]
        }

        result = sg_ops.get_security_groups("vpc-123")

        assert result["total_count"] == 1
        assert len(result["security_groups"]) == 1
        assert result["security_groups"][0]["group_id"] == "sg-123"
        assert result["security_groups"][0]["group_name"] == "web-sg"
        assert result["security_groups"][0]["name"] == "Web SG"

    def test_get_security_groups_empty(self, sg_ops: SecurityGroupOperations, mock_aws_client: AWSClient) -> None:
        """Test VPC with no security groups."""
        mock_aws_client.describe_security_groups.return_value = {"SecurityGroups": []}

        result = sg_ops.get_security_groups("vpc-123")

        assert result["total_count"] == 0
        assert result["security_groups"] == []

    def test_get_security_groups_with_rules(self, sg_ops: SecurityGroupOperations, mock_aws_client: AWSClient) -> None:
        """Test security group with multiple rules."""
        mock_aws_client.describe_security_groups.return_value = {
            "SecurityGroups": [{
                "GroupId": "sg-123",
                "GroupName": "app-sg",
                "Description": "Application security group",
                "VpcId": "vpc-123",
                "IpPermissions": [
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 443,
                        "ToPort": 443,
                        "IpRanges": [{"CidrIp": "10.0.0.0/16", "Description": "Internal"}],
                    },
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 22,
                        "ToPort": 22,
                        "UserIdGroupPairs": [{"GroupId": "sg-456"}],
                    },
                ],
                "IpPermissionsEgress": [{
                    "IpProtocol": "-1",
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                }],
            }]
        }

        result = sg_ops.get_security_groups("vpc-123")

        assert len(result["security_groups"][0]["inbound_rules"]) == 2
        assert len(result["security_groups"][0]["outbound_rules"]) == 1
