"""Direct Connect Virtual Interface operations."""

from __future__ import annotations

from typing import Any

from loguru import logger

from vpc_reporter.aws.client import AWSClient


class DirectConnectVIFOperations:
    """Operations for Direct Connect Virtual Interface resources."""

    def __init__(self, aws_client: AWSClient) -> None:
        """Initialize Direct Connect VIF operations.

        Args:
            aws_client: AWS client instance
        """
        self.client = aws_client

    def get_virtual_interfaces(self) -> dict[str, Any]:
        """Get all Direct Connect virtual interfaces in the region.

        Note: Uses DirectConnect API, not EC2 API.
        VIFs are not VPC-specific, so we get all in the region.

        Returns:
            Dictionary with virtual interface data
        """
        logger.info("Getting Direct Connect virtual interfaces")

        try:
            response = self.client.describe_virtual_interfaces()
        except Exception as e:
            logger.warning(
                f"Failed to get Direct Connect VIFs (may not have permissions): {e}"
            )
            return {
                "total_count": 0,
                "virtual_interfaces": [],
                "error": str(e),
            }

        virtual_interfaces = response.get("virtualInterfaces", [])

        processed_vifs = []
        for vif in virtual_interfaces:
            # Parse route filter prefixes
            route_filters = []
            for prefix in vif.get("routeFilterPrefixes", []):
                route_filters.append(prefix.get("cidr"))

            # **CRITICAL**: Parse BGP peers for BGP status (up/down)
            bgp_peers = []
            bgp_status_summary = {"up": 0, "down": 0, "unknown": 0}
            for peer in vif.get("bgpPeers", []):
                bgp_status = peer.get("bgpStatus", "unknown").lower()
                bgp_status_summary[bgp_status] = (
                    bgp_status_summary.get(bgp_status, 0) + 1
                )

                bgp_peers.append(
                    {
                        "bgp_peer_id": peer.get("bgpPeerId"),
                        "asn": peer.get("asn"),
                        "auth_key": peer.get("authKey"),
                        "address_family": peer.get("addressFamily"),
                        "amazon_address": peer.get("amazonAddress"),
                        "customer_address": peer.get("customerAddress"),
                        "bgp_peer_state": peer.get("bgpPeerState"),
                        "bgp_status": peer.get("bgpStatus"),  # up, down, unknown
                        "aws_device_v2": peer.get("awsDeviceV2"),
                        "aws_logical_device_id": peer.get("awsLogicalDeviceId"),
                    }
                )

            processed_vifs.append(
                {
                    "virtual_interface_id": vif["virtualInterfaceId"],
                    "virtual_interface_name": vif.get("virtualInterfaceName"),
                    "virtual_interface_type": vif.get(
                        "virtualInterfaceType"
                    ),  # private, public, transit
                    "virtual_interface_state": vif.get("virtualInterfaceState"),
                    "vlan": vif.get("vlan"),
                    "location": vif.get("location"),
                    "connection_id": vif.get("connectionId"),
                    "owner_account": vif.get("ownerAccount"),
                    "region": vif.get("region"),
                    # BGP configuration
                    "asn": vif.get("asn"),
                    "amazon_side_asn": vif.get("amazonSideAsn"),
                    "auth_key": vif.get("authKey"),
                    "amazon_address": vif.get("amazonAddress"),
                    "customer_address": vif.get("customerAddress"),
                    "address_family": vif.get("addressFamily"),
                    # Network configuration
                    "mtu": vif.get("mtu"),
                    "jumbo_frame_capable": vif.get("jumboFrameCapable", False),
                    "aws_device_v2": vif.get("awsDeviceV2"),
                    "aws_logical_device_id": vif.get("awsLogicalDeviceId"),
                    # Gateway associations
                    "virtual_gateway_id": vif.get("virtualGatewayId"),
                    "direct_connect_gateway_id": vif.get("directConnectGatewayId"),
                    # Route filters
                    "route_filter_prefixes": route_filters,
                    "route_filter_count": len(route_filters),
                    # **CRITICAL**: BGP peer status
                    "bgp_peers": bgp_peers,
                    "bgp_peer_count": len(bgp_peers),
                    "bgp_status_summary": bgp_status_summary,
                    "bgp_sessions_up": bgp_status_summary.get("up", 0),
                    "bgp_sessions_down": bgp_status_summary.get("down", 0),
                    "all_bgp_sessions_up": bgp_status_summary.get("up", 0)
                    == len(bgp_peers)
                    and len(bgp_peers) > 0,
                    # Additional fields
                    "customer_router_config": vif.get("customerRouterConfig"),
                    "site_link_enabled": vif.get("siteLinkEnabled", False),
                    # Metadata
                    "tags": vif.get("tags", []),
                    "name": self._get_tag_value(vif.get("tags", []), "Name"),
                }
            )

        logger.info(f"Found {len(processed_vifs)} Direct Connect virtual interfaces")

        return {
            "total_count": len(processed_vifs),
            "virtual_interfaces": processed_vifs,
            "raw_data": virtual_interfaces,
        }

    @staticmethod
    def _get_tag_value(tags: list[dict[str, str]], key: str) -> str | None:
        """Extract tag value by key."""
        for tag in tags:
            if tag.get("key") == key:  # Note: DirectConnect uses lowercase 'key'
                return tag.get("value")
        return None
