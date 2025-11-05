"""Virtual Private Gateway operations."""

from __future__ import annotations

from typing import Any

from loguru import logger

from vpc_reporter.aws.client import AWSClient


class VirtualPrivateGatewayOperations:
    """Operations for Virtual Private Gateway resources."""

    def __init__(self, aws_client: AWSClient) -> None:
        """Initialize virtual private gateway operations.

        Args:
            aws_client: AWS client instance
        """
        self.client = aws_client

    def get_vpn_gateways(self, vpc_id: str) -> dict[str, Any]:
        """Get all VPN gateways attached to a VPC.

        Args:
            vpc_id: VPC ID

        Returns:
            Dictionary with VPN gateway data
        """
        logger.info(f"Getting VPN gateways for VPC {vpc_id}")

        response = self.client.describe_vpn_gateways(
            Filters=[{"Name": "attachment.vpc-id", "Values": [vpc_id]}]
        )

        vpn_gateways = response.get("VpnGateways", [])

        processed_vgws = []
        for vgw in vpn_gateways:
            # Parse VPC attachments
            attachments = []
            for attachment in vgw.get("VpcAttachments", []):
                attachments.append(
                    {
                        "vpc_id": attachment.get("VpcId"),
                        "state": attachment.get("State"),
                    }
                )

            processed_vgws.append(
                {
                    "vpn_gateway_id": vgw["VpnGatewayId"],
                    "state": vgw.get("State"),
                    "type": vgw.get("Type", "ipsec.1"),
                    "availability_zone": vgw.get("AvailabilityZone"),
                    "vpc_attachments": attachments,
                    "attached_vpc_id": (
                        attachments[0]["vpc_id"] if attachments else None
                    ),
                    "attachment_state": (
                        attachments[0]["state"] if attachments else None
                    ),
                    "amazon_side_asn": vgw.get("AmazonSideAsn"),
                    "tags": vgw.get("Tags", []),
                    "name": self._get_tag_value(vgw.get("Tags", []), "Name"),
                }
            )

        logger.info(f"Found {len(processed_vgws)} VPN gateways")

        return {
            "total_count": len(processed_vgws),
            "vpn_gateways": processed_vgws,
            "raw_data": vpn_gateways,
        }

    @staticmethod
    def _get_tag_value(tags: list[dict[str, str]], key: str) -> str | None:
        """Extract tag value by key."""
        for tag in tags:
            if tag.get("Key") == key:
                return tag.get("Value")
        return None
