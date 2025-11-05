"""VPC operations."""

from __future__ import annotations

from typing import Any

from loguru import logger

from vpc_reporter.aws.client import AWSClient
from vpc_reporter.aws.exceptions import VPCNotFoundError


class VPCOperations:
    """Operations for VPC resources."""

    def __init__(self, aws_client: AWSClient) -> None:
        """Initialize VPC operations.

        Args:
            aws_client: AWS client instance
        """
        self.client = aws_client

    def list_vpcs(self) -> list[dict[str, Any]]:
        """List all VPCs in the region.

        Returns:
            List of VPC dictionaries with basic info
        """
        logger.info("Listing VPCs")

        response = self.client.describe_vpcs()
        vpcs = []

        for vpc in response.get("Vpcs", []):
            vpc_info = {
                "vpc_id": vpc["VpcId"],
                "cidr_block": vpc["CidrBlock"],
                "state": vpc["State"],
                "is_default": vpc.get("IsDefault", False),
                "name": self._get_tag_value(vpc.get("Tags", []), "Name"),
            }
            vpcs.append(vpc_info)

        logger.info(f"Found {len(vpcs)} VPCs")
        return vpcs

    def get_vpc_details(self, vpc_id: str) -> dict[str, Any]:
        """Get detailed VPC information.

        Args:
            vpc_id: VPC ID

        Returns:
            VPC details dictionary

        Raises:
            VPCNotFoundError: If VPC not found
        """
        logger.info(f"Getting VPC details for {vpc_id}")

        response = self.client.describe_vpcs(VpcIds=[vpc_id])
        vpcs = response.get("Vpcs", [])

        if not vpcs:
            raise VPCNotFoundError(f"VPC {vpc_id} not found")

        vpc = vpcs[0]

        # Parse IPv6 CIDR block associations with full details
        ipv6_associations = []
        for assoc in vpc.get("Ipv6CidrBlockAssociationSet", []):
            ipv6_associations.append(
                {
                    "association_id": assoc.get("AssociationId"),
                    "ipv6_cidr_block": assoc.get("Ipv6CidrBlock"),
                    "ipv6_pool": assoc.get("Ipv6Pool"),
                    "network_border_group": assoc.get("NetworkBorderGroup"),
                    "ipv6_address_attribute": assoc.get("Ipv6AddressAttribute"),
                    "ip_source": assoc.get("IpSource"),
                    "state": assoc.get("Ipv6CidrBlockState", {}).get("State"),
                    "status_message": assoc.get("Ipv6CidrBlockState", {}).get(
                        "StatusMessage"
                    ),
                }
            )

        # Parse IPv4 CIDR block associations with full details
        cidr_associations = []
        for assoc in vpc.get("CidrBlockAssociationSet", []):
            cidr_associations.append(
                {
                    "association_id": assoc.get("AssociationId"),
                    "cidr_block": assoc.get("CidrBlock"),
                    "state": assoc.get("CidrBlockState", {}).get("State"),
                    "status_message": assoc.get("CidrBlockState", {}).get(
                        "StatusMessage"
                    ),
                }
            )

        return {
            "vpc_id": vpc["VpcId"],
            "cidr_block": vpc["CidrBlock"],
            "state": vpc["State"],
            "is_default": vpc.get("IsDefault", False),
            "instance_tenancy": vpc.get("InstanceTenancy", "default"),
            "dhcp_options_id": vpc.get("DhcpOptionsId"),
            "owner_id": vpc.get("OwnerId"),
            # IPv6 configuration with full details
            "ipv6_cidr_block_associations": ipv6_associations,
            "ipv6_cidr_blocks": [
                assoc["ipv6_cidr_block"]
                for assoc in ipv6_associations
                if assoc["ipv6_cidr_block"]
            ],
            # IPv4 CIDR associations with full details
            "cidr_block_associations": cidr_associations,
            "additional_cidr_blocks": [
                assoc["cidr_block"]
                for assoc in cidr_associations
                if assoc["cidr_block"] != vpc["CidrBlock"]
            ],
            # Tags
            "tags": vpc.get("Tags", []),
            "name": self._get_tag_value(vpc.get("Tags", []), "Name"),
            "raw_data": vpc,
        }

    @staticmethod
    def _get_tag_value(tags: list[dict[str, str]], key: str) -> str | None:
        """Extract tag value by key.

        Args:
            tags: List of tag dictionaries
            key: Tag key to find

        Returns:
            Tag value or None
        """
        for tag in tags:
            if tag.get("Key") == key:
                return tag.get("Value")
        return None
