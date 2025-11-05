"""Elastic IP operations."""

from __future__ import annotations

from typing import Any

from loguru import logger

from vpc_reporter.aws.client import AWSClient


class ElasticIPOperations:
    """Operations for Elastic IP resources."""

    def __init__(self, aws_client: AWSClient) -> None:
        """Initialize Elastic IP operations.

        Args:
            aws_client: AWS client instance
        """
        self.client = aws_client

    def get_elastic_ips(self, vpc_id: str) -> dict[str, Any]:
        """Get all Elastic IPs associated with a VPC.

        Note: EIPs don't have a direct VPC filter, so we get all VPC-domain EIPs
        and then filter by checking associations.

        Args:
            vpc_id: VPC ID

        Returns:
            Dictionary with Elastic IP data
        """
        logger.info(f"Getting Elastic IPs for VPC {vpc_id}")

        # Get all VPC-domain Elastic IPs
        response = self.client.describe_addresses(
            Filters=[{"Name": "domain", "Values": ["vpc"]}]
        )

        addresses = response.get("Addresses", [])

        # We'll get all EIPs and show which ones are in this VPC
        # (via network interface association)
        processed_eips = []

        for addr in addresses:
            eip_data = {
                "public_ip": addr.get("PublicIp"),
                "allocation_id": addr.get("AllocationId"),
                "domain": addr.get("Domain", "vpc"),
                "instance_id": addr.get("InstanceId"),
                "association_id": addr.get("AssociationId"),
                "network_interface_id": addr.get("NetworkInterfaceId"),
                "network_interface_owner_id": addr.get("NetworkInterfaceOwnerId"),
                "private_ip_address": addr.get("PrivateIpAddress"),
                "network_border_group": addr.get("NetworkBorderGroup"),
                "customer_owned_ip": addr.get("CustomerOwnedIp"),
                "customer_owned_ipv4_pool": addr.get("CustomerOwnedIpv4Pool"),
                "carrier_ip": addr.get("CarrierIp"),
                "public_ipv4_pool": addr.get("PublicIpv4Pool", "amazon"),
                "is_associated": bool(addr.get("AssociationId")),
                "tags": addr.get("Tags", []),
                "name": self._get_tag_value(addr.get("Tags", []), "Name"),
            }

            processed_eips.append(eip_data)

            # Note: We can't directly filter by VPC, but we collect all for the report
            # The user can see which EIPs are in use vs available

        logger.info(f"Found {len(processed_eips)} Elastic IPs (VPC domain)")

        return {
            "total_count": len(processed_eips),
            "associated_count": len([e for e in processed_eips if e["is_associated"]]),
            "unassociated_count": len(
                [e for e in processed_eips if not e["is_associated"]]
            ),
            "elastic_ips": processed_eips,
            "raw_data": addresses,
        }

    @staticmethod
    def _get_tag_value(tags: list[dict[str, str]], key: str) -> str | None:
        """Extract tag value by key."""
        for tag in tags:
            if tag.get("Key") == key:
                return tag.get("Value")
        return None
