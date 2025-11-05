"""VPN Connection operations."""

from __future__ import annotations

from typing import Any

from loguru import logger

from vpc_reporter.aws.client import AWSClient


class VPNConnectionOperations:
    """Operations for VPN Connection resources."""

    def __init__(self, aws_client: AWSClient) -> None:
        """Initialize VPN connection operations.

        Args:
            aws_client: AWS client instance
        """
        self.client = aws_client

    def get_vpn_connections(self) -> dict[str, Any]:
        """Get all VPN connections in the region.

        Note: VPN connections can be associated with VGW or TGW, not directly with VPC.
        We get all VPN connections in the region.

        Returns:
            Dictionary with VPN connection data
        """
        logger.info("Getting VPN connections")

        response = self.client.describe_vpn_connections()

        vpn_connections = response.get("VpnConnections", [])

        processed_vpns = []
        for vpn in vpn_connections:
            # Parse options
            options = vpn.get("Options", {})

            # Parse tunnel options (detailed IPSec config)
            tunnel_options = []
            for tunnel in options.get("TunnelOptions", []):
                tunnel_options.append(
                    {
                        "outside_ip_address": tunnel.get("OutsideIpAddress"),
                        "tunnel_inside_cidr": tunnel.get("TunnelInsideCidr"),
                        "tunnel_inside_ipv6_cidr": tunnel.get("TunnelInsideIpv6Cidr"),
                        "pre_shared_key": tunnel.get("PreSharedKey"),
                        "phase1_lifetime_seconds": tunnel.get("Phase1LifetimeSeconds"),
                        "phase2_lifetime_seconds": tunnel.get("Phase2LifetimeSeconds"),
                        "rekey_margin_time_seconds": tunnel.get(
                            "RekeyMarginTimeSeconds"
                        ),
                        "rekey_fuzz_percentage": tunnel.get("RekeyFuzzPercentage"),
                        "replay_window_size": tunnel.get("ReplayWindowSize"),
                        "dpd_timeout_seconds": tunnel.get("DpdTimeoutSeconds"),
                        "dpd_timeout_action": tunnel.get("DpdTimeoutAction"),
                        "startup_action": tunnel.get("StartupAction"),
                    }
                )

            # Parse static routes
            routes = []
            for route in vpn.get("Routes", []):
                routes.append(
                    {
                        "destination_cidr_block": route.get("DestinationCidrBlock"),
                        "source": route.get("Source"),
                        "state": route.get("State"),
                    }
                )

            # **CRITICAL**: Parse VGW telemetry for tunnel status (UP/DOWN)
            telemetry = []
            tunnel_status_summary = {"up": 0, "down": 0, "unknown": 0}
            for telem in vpn.get("VgwTelemetry", []):
                status = telem.get("Status", "unknown").lower()
                tunnel_status_summary[status] = tunnel_status_summary.get(status, 0) + 1

                telemetry.append(
                    {
                        "outside_ip_address": telem.get("OutsideIpAddress"),
                        "status": telem.get("Status"),  # UP or DOWN
                        "last_status_change": telem.get("LastStatusChange"),
                        "status_message": telem.get("StatusMessage"),
                        "accepted_route_count": telem.get("AcceptedRouteCount", 0),
                        "certificate_arn": telem.get("CertificateArn"),
                    }
                )

            # Determine gateway type
            gateway_type = "unknown"
            gateway_id = None
            if vpn.get("VpnGatewayId"):
                gateway_type = "vpn_gateway"
                gateway_id = vpn.get("VpnGatewayId")
            elif vpn.get("TransitGatewayId"):
                gateway_type = "transit_gateway"
                gateway_id = vpn.get("TransitGatewayId")

            processed_vpns.append(
                {
                    "vpn_connection_id": vpn["VpnConnectionId"],
                    "state": vpn.get("State"),
                    "type": vpn.get("Type", "ipsec.1"),
                    "category": vpn.get("Category", "VPN"),
                    "customer_gateway_id": vpn.get("CustomerGatewayId"),
                    "vpn_gateway_id": vpn.get("VpnGatewayId"),
                    "transit_gateway_id": vpn.get("TransitGatewayId"),
                    "gateway_type": gateway_type,
                    "gateway_id": gateway_id,
                    "core_network_arn": vpn.get("CoreNetworkArn"),
                    "core_network_attachment_arn": vpn.get("CoreNetworkAttachmentArn"),
                    "gateway_association_state": vpn.get("GatewayAssociationState"),
                    # Options
                    "enable_acceleration": options.get("EnableAcceleration", False),
                    "static_routes_only": options.get("StaticRoutesOnly", False),
                    "local_ipv4_network_cidr": options.get("LocalIpv4NetworkCidr"),
                    "remote_ipv4_network_cidr": options.get("RemoteIpv4NetworkCidr"),
                    "local_ipv6_network_cidr": options.get("LocalIpv6NetworkCidr"),
                    "remote_ipv6_network_cidr": options.get("RemoteIpv6NetworkCidr"),
                    "outside_ip_address_type": options.get("OutsideIpAddressType"),
                    "transport_transit_gateway_attachment_id": options.get(
                        "TransportTransitGatewayAttachmentId"
                    ),
                    "tunnel_inside_ip_version": options.get(
                        "TunnelInsideIpVersion", "ipv4"
                    ),
                    # Tunnel details
                    "tunnel_options": tunnel_options,
                    "tunnel_count": len(tunnel_options),
                    # Routes
                    "routes": routes,
                    "route_count": len(routes),
                    # **CRITICAL**: Tunnel status
                    "vgw_telemetry": telemetry,
                    "tunnel_status_summary": tunnel_status_summary,
                    "tunnels_up": tunnel_status_summary.get("up", 0),
                    "tunnels_down": tunnel_status_summary.get("down", 0),
                    "all_tunnels_up": tunnel_status_summary.get("up", 0)
                    == len(telemetry)
                    and len(telemetry) > 0,
                    # Metadata
                    "tags": vpn.get("Tags", []),
                    "name": self._get_tag_value(vpn.get("Tags", []), "Name"),
                }
            )

        logger.info(f"Found {len(processed_vpns)} VPN connections")

        return {
            "total_count": len(processed_vpns),
            "vpn_connections": processed_vpns,
            "raw_data": vpn_connections,
        }

    @staticmethod
    def _get_tag_value(tags: list[dict[str, str]], key: str) -> str | None:
        """Extract tag value by key."""
        for tag in tags:
            if tag.get("Key") == key:
                return tag.get("Value")
        return None
