"""Security group operations."""

from __future__ import annotations

from typing import Any

from loguru import logger

from vpc_reporter.aws.client import AWSClient


class SecurityGroupOperations:
    """Operations for Security Group resources."""

    def __init__(self, aws_client: AWSClient) -> None:
        """Initialize security group operations.

        Args:
            aws_client: AWS client instance
        """
        self.client = aws_client

    def get_security_groups(self, vpc_id: str) -> dict[str, Any]:
        """Get all security groups for a VPC.

        Args:
            vpc_id: VPC ID

        Returns:
            Dictionary with security group data
        """
        logger.info(f"Getting security groups for VPC {vpc_id}")

        response = self.client.describe_security_groups(
            Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )

        security_groups = response.get("SecurityGroups", [])

        processed_sgs = []
        for sg in security_groups:
            # Parse inbound rules with full details
            inbound_rules = self._parse_rules(sg.get("IpPermissions", []))

            # Parse outbound rules with full details
            outbound_rules = self._parse_rules(sg.get("IpPermissionsEgress", []))

            processed_sgs.append(
                {
                    "group_id": sg["GroupId"],
                    "group_name": sg["GroupName"],
                    "description": sg.get("Description", ""),
                    "vpc_id": sg.get("VpcId"),
                    "owner_id": sg.get("OwnerId"),
                    "inbound_rules_count": len(inbound_rules),
                    "outbound_rules_count": len(outbound_rules),
                    "inbound_rules": inbound_rules,
                    "outbound_rules": outbound_rules,
                    "inbound_rules_raw": sg.get("IpPermissions", []),
                    "outbound_rules_raw": sg.get("IpPermissionsEgress", []),
                    "tags": sg.get("Tags", []),
                    "name": self._get_tag_value(sg.get("Tags", []), "Name"),
                }
            )

        logger.info(f"Found {len(processed_sgs)} security groups")

        return {
            "total_count": len(processed_sgs),
            "security_groups": processed_sgs,
            "raw_data": security_groups,
        }

    def _parse_rules(self, permissions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Parse security group rules with full details.

        Args:
            permissions: List of IpPermissions or IpPermissionsEgress

        Returns:
            List of parsed rules with all details
        """
        parsed_rules = []

        for perm in permissions:
            protocol = perm.get("IpProtocol", "-1")
            from_port = perm.get("FromPort", "All")
            to_port = perm.get("ToPort", "All")

            # Format port range
            if protocol == "-1":
                port_range = "All"
                protocol_name = "All"
            elif from_port == to_port:
                port_range = str(from_port)
                protocol_name = self._get_protocol_name(protocol)
            else:
                port_range = f"{from_port}-{to_port}"
                protocol_name = self._get_protocol_name(protocol)

            # Parse IPv4 ranges
            for ip_range in perm.get("IpRanges", []):
                parsed_rules.append(
                    {
                        "type": "IPv4",
                        "protocol": protocol_name,
                        "port_range": port_range,
                        "source": ip_range.get("CidrIp", ""),
                        "description": ip_range.get("Description", ""),
                    }
                )

            # Parse IPv6 ranges
            for ipv6_range in perm.get("Ipv6Ranges", []):
                parsed_rules.append(
                    {
                        "type": "IPv6",
                        "protocol": protocol_name,
                        "port_range": port_range,
                        "source": ipv6_range.get("CidrIpv6", ""),
                        "description": ipv6_range.get("Description", ""),
                    }
                )

            # Parse prefix lists
            for prefix_list in perm.get("PrefixListIds", []):
                parsed_rules.append(
                    {
                        "type": "Prefix List",
                        "protocol": protocol_name,
                        "port_range": port_range,
                        "source": prefix_list.get("PrefixListId", ""),
                        "description": prefix_list.get("Description", ""),
                    }
                )

            # Parse referenced security groups
            for user_id_group in perm.get("UserIdGroupPairs", []):
                parsed_rules.append(
                    {
                        "type": "Security Group",
                        "protocol": protocol_name,
                        "port_range": port_range,
                        "source": user_id_group.get("GroupId", ""),
                        "description": user_id_group.get("Description", ""),
                    }
                )

        return parsed_rules

    @staticmethod
    def _get_protocol_name(protocol: str) -> str:
        """Convert protocol number to name.

        Args:
            protocol: Protocol number or name

        Returns:
            Protocol name
        """
        protocol_map = {
            "-1": "All",
            "1": "ICMP",
            "6": "TCP",
            "17": "UDP",
            "58": "ICMPv6",
        }
        return protocol_map.get(protocol, protocol)

    @staticmethod
    def _get_tag_value(tags: list[dict[str, str]], key: str) -> str | None:
        """Extract tag value by key."""
        for tag in tags:
            if tag.get("Key") == key:
                return tag.get("Value")
        return None
