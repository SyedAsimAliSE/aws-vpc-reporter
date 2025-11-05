"""Unit tests for VPN Connection operations."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from vpc_reporter.aws.client import AWSClient
from vpc_reporter.operations.vpn_ops import VPNConnectionOperations


@pytest.fixture
def mock_aws_client() -> AWSClient:
    """Create a mock AWS client."""
    client = MagicMock(spec=AWSClient)
    client.region = "us-east-1"
    return client


@pytest.fixture
def vpn_ops(mock_aws_client: AWSClient) -> VPNConnectionOperations:
    """Create VPN Connection operations instance."""
    return VPNConnectionOperations(mock_aws_client)


class TestVPNConnectionOperations:
    """Test VPN Connection operations class."""

    def test_get_vpn_connections_success(self, vpn_ops: VPNConnectionOperations, mock_aws_client: AWSClient) -> None:
        """Test successful VPN connection retrieval."""
        mock_aws_client.describe_vpn_connections.return_value = {
            "VpnConnections": [{
                "VpnConnectionId": "vpn-123",
                "State": "available",
                "Type": "ipsec.1",
                "CustomerGatewayId": "cgw-123",
                "VpnGatewayId": "vgw-123",
                "VgwTelemetry": [
                    {
                        "OutsideIpAddress": "52.1.2.3",
                        "Status": "UP",
                        "LastStatusChange": "2024-01-01T00:00:00Z",
                    },
                    {
                        "OutsideIpAddress": "52.1.2.4",
                        "Status": "UP",
                        "LastStatusChange": "2024-01-01T00:00:00Z",
                    },
                ],
                "Tags": [{"Key": "Name", "Value": "Site-to-Site VPN"}],
            }]
        }

        result = vpn_ops.get_vpn_connections()

        assert result["total_count"] == 1
        assert len(result["vpn_connections"]) == 1
        assert result["vpn_connections"][0]["vpn_connection_id"] == "vpn-123"
        assert result["vpn_connections"][0]["state"] == "available"
        assert result["vpn_connections"][0]["name"] == "Site-to-Site VPN"
        assert len(result["vpn_connections"][0]["vgw_telemetry"]) == 2

    def test_get_vpn_connections_empty(self, vpn_ops: VPNConnectionOperations, mock_aws_client: AWSClient) -> None:
        """Test no VPN connections."""
        mock_aws_client.describe_vpn_connections.return_value = {"VpnConnections": []}

        result = vpn_ops.get_vpn_connections()

        assert result["total_count"] == 0
        assert result["vpn_connections"] == []

    def test_get_vpn_connections_tunnel_status(self, vpn_ops: VPNConnectionOperations, mock_aws_client: AWSClient) -> None:
        """Test VPN tunnel status parsing."""
        mock_aws_client.describe_vpn_connections.return_value = {
            "VpnConnections": [{
                "VpnConnectionId": "vpn-mixed",
                "State": "available",
                "Type": "ipsec.1",
                "VgwTelemetry": [
                    {"OutsideIpAddress": "52.1.2.3", "Status": "UP"},
                    {"OutsideIpAddress": "52.1.2.4", "Status": "DOWN"},
                ],
            }]
        }

        result = vpn_ops.get_vpn_connections()

        telemetry = result["vpn_connections"][0]["vgw_telemetry"]
        assert telemetry[0]["status"] == "UP"
        assert telemetry[1]["status"] == "DOWN"
