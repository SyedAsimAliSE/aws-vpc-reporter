"""Subnet operations."""

from __future__ import annotations

from typing import Any

from loguru import logger

from vpc_reporter.aws.client import AWSClient


class SubnetOperations:
    """Operations for Subnet resources."""

    def __init__(self, aws_client: AWSClient) -> None:
        """Initialize subnet operations.

        Args:
            aws_client: AWS client instance
        """
        self.client = aws_client

    def get_subnets(self, vpc_id: str) -> dict[str, Any]:
        """Get all subnets for a VPC.

        Args:
            vpc_id: VPC ID

        Returns:
            Dictionary with subnet data
        """
        logger.info(f"Getting subnets for VPC {vpc_id}")

        response = self.client.describe_subnets(
            Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )

        subnets = response.get("Subnets", [])

        processed_subnets = []
        for subnet in subnets:
            # Parse IPv6 CIDR blocks
            ipv6_cidrs = [
                {
                    "ipv6_cidr_block": assoc.get("Ipv6CidrBlock"),
                    "association_id": assoc.get("AssociationId"),
                    "state": assoc.get("Ipv6CidrBlockState", {}).get("State"),
                }
                for assoc in subnet.get("Ipv6CidrBlockAssociationSet", [])
            ]

            # Parse private DNS name options
            dns_options = subnet.get("PrivateDnsNameOptionsOnLaunch", {})

            processed_subnets.append({
                "subnet_id": subnet["SubnetId"],
                "subnet_arn": subnet.get("SubnetArn"),
                "cidr_block": subnet["CidrBlock"],
                "availability_zone": subnet["AvailabilityZone"],
                "availability_zone_id": subnet.get("AvailabilityZoneId"),
                "available_ip_count": subnet.get("AvailableIpAddressCount", 0),
                "map_public_ip": subnet.get("MapPublicIpOnLaunch", False),
                "state": subnet["State"],
                "default_for_az": subnet.get("DefaultForAz", False),
                "vpc_id": subnet.get("VpcId"),
                "owner_id": subnet.get("OwnerId"),
                # IPv6 configuration
                "assign_ipv6_on_creation": subnet.get("AssignIpv6AddressOnCreation", False),
                "ipv6_native": subnet.get("Ipv6Native", False),
                "ipv6_cidr_blocks": ipv6_cidrs,
                "enable_dns64": subnet.get("EnableDns64", False),
                # Private DNS configuration
                "private_dns_hostname_type": dns_options.get("HostnameType", "ip-name"),
                "enable_resource_name_dns_a_record": dns_options.get("EnableResourceNameDnsARecord", False),
                "enable_resource_name_dns_aaaa_record": dns_options.get("EnableResourceNameDnsAAAARecord", False),
                # Customer-owned IP
                "map_customer_owned_ip": subnet.get("MapCustomerOwnedIpOnLaunch", False),
                "customer_owned_ipv4_pool": subnet.get("CustomerOwnedIpv4Pool"),
                # Outpost
                "outpost_arn": subnet.get("OutpostArn"),
                "enable_lni_at_device_index": subnet.get("EnableLniAtDeviceIndex"),
                # Tags
                "name": self._get_tag_value(subnet.get("Tags", []), "Name"),
                "tags": subnet.get("Tags", []),
            })

        logger.info(f"Found {len(processed_subnets)} subnets")

        return {
            "total_count": len(processed_subnets),
            "subnets": processed_subnets,
            "raw_data": subnets,
        }

    @staticmethod
    def _get_tag_value(tags: list[dict[str, str]], key: str) -> str | None:
        """Extract tag value by key."""
        for tag in tags:
            if tag.get("Key") == key:
                return tag.get("Value")
        return None
