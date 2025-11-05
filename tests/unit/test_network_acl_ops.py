"""Unit tests for Network ACL operations."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from vpc_reporter.aws.client import AWSClient
from vpc_reporter.operations.network_acl_ops import NetworkACLOperations


@pytest.fixture
def mock_aws_client() -> AWSClient:
    """Create a mock AWS client."""
    client = MagicMock(spec=AWSClient)
    client.region = "us-east-1"
    return client


@pytest.fixture
def nacl_ops(mock_aws_client: AWSClient) -> NetworkACLOperations:
    """Create Network ACL operations instance."""
    return NetworkACLOperations(mock_aws_client)


class TestNetworkACLOperations:
    """Test Network ACL operations class."""

    def test_get_network_acls_success(self, nacl_ops: NetworkACLOperations, mock_aws_client: AWSClient) -> None:
        """Test successful network ACL retrieval."""
        mock_aws_client.describe_network_acls.return_value = {
            "NetworkAcls": [{
                "NetworkAclId": "acl-123",
                "VpcId": "vpc-123",
                "IsDefault": False,
                "Entries": [
                    {
                        "RuleNumber": 100,
                        "Protocol": "6",
                        "RuleAction": "allow",
                        "Egress": False,
                        "CidrBlock": "0.0.0.0/0",
                        "PortRange": {"From": 80, "To": 80},
                    }
                ],
                "Associations": [{
                    "NetworkAclAssociationId": "aclassoc-123",
                    "SubnetId": "subnet-123",
                }],
                "Tags": [{"Key": "Name", "Value": "Custom NACL"}],
            }]
        }

        result = nacl_ops.get_network_acls("vpc-123")

        assert result["total_count"] == 1
        assert len(result["network_acls"]) == 1
        assert result["network_acls"][0]["network_acl_id"] == "acl-123"
        assert result["network_acls"][0]["name"] == "Custom NACL"
        assert result["network_acls"][0]["is_default"] is False

    def test_get_network_acls_empty(self, nacl_ops: NetworkACLOperations, mock_aws_client: AWSClient) -> None:
        """Test VPC with no network ACLs."""
        mock_aws_client.describe_network_acls.return_value = {"NetworkAcls": []}

        result = nacl_ops.get_network_acls("vpc-123")

        assert result["total_count"] == 0
        assert result["network_acls"] == []

    def test_get_network_acls_default(self, nacl_ops: NetworkACLOperations, mock_aws_client: AWSClient) -> None:
        """Test default network ACL."""
        mock_aws_client.describe_network_acls.return_value = {
            "NetworkAcls": [{
                "NetworkAclId": "acl-default",
                "VpcId": "vpc-123",
                "IsDefault": True,
                "Entries": [],
                "Associations": [],
            }]
        }

        result = nacl_ops.get_network_acls("vpc-123")

        assert result["network_acls"][0]["is_default"] is True
