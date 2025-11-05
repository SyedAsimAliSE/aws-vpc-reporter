"""Network ACL operations."""

from __future__ import annotations

from typing import Any

from loguru import logger

from vpc_reporter.aws.client import AWSClient


class NetworkACLOperations:
    """Operations for Network ACL resources."""

    def __init__(self, aws_client: AWSClient) -> None:
        """Initialize network ACL operations.

        Args:
            aws_client: AWS client instance
        """
        self.client = aws_client

    def get_network_acls(self, vpc_id: str) -> dict[str, Any]:
        """Get all network ACLs for a VPC.

        Args:
            vpc_id: VPC ID

        Returns:
            Dictionary with network ACL data
        """
        logger.info(f"Getting network ACLs for VPC {vpc_id}")

        response = self.client.describe_network_acls(
            Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )

        network_acls = response.get("NetworkAcls", [])

        processed_acls = []
        for nacl in network_acls:
            # Get associated subnets
            associations = []
            for assoc in nacl.get("Associations", []):
                associations.append({
                    "network_acl_association_id": assoc.get("NetworkAclAssociationId"),
                    "subnet_id": assoc.get("SubnetId"),
                })

            # Parse rules with full details
            entries = nacl.get("Entries", [])
            inbound_rules = self._parse_rules([e for e in entries if not e.get("Egress", False)])
            outbound_rules = self._parse_rules([e for e in entries if e.get("Egress", False)])

            processed_acls.append({
                "network_acl_id": nacl["NetworkAclId"],
                "vpc_id": nacl.get("VpcId"),
                "owner_id": nacl.get("OwnerId"),
                "is_default": nacl.get("IsDefault", False),
                "associations": associations,
                "associated_subnet_count": len(associations),
                "inbound_rules_count": len(inbound_rules),
                "outbound_rules_count": len(outbound_rules),
                "inbound_rules": inbound_rules,
                "outbound_rules": outbound_rules,
                "entries_raw": entries,
                "tags": nacl.get("Tags", []),
                "name": self._get_tag_value(nacl.get("Tags", []), "Name"),
            })

        logger.info(f"Found {len(processed_acls)} network ACLs")

        return {
            "total_count": len(processed_acls),
            "network_acls": processed_acls,
            "raw_data": network_acls,
        }

    def _parse_rules(self, entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Parse NACL rules with full details.

        Args:
            entries: List of NACL entries

        Returns:
            List of parsed rules sorted by rule number
        """
        parsed_rules = []

        for entry in entries:
            rule_number = entry.get("RuleNumber", 0)
            protocol = entry.get("Protocol", "-1")
            rule_action = entry.get("RuleAction", "").upper()
            cidr_block = entry.get("CidrBlock", entry.get("Ipv6CidrBlock", ""))

            # Get port range
            port_range_obj = entry.get("PortRange", {})
            if port_range_obj:
                from_port = port_range_obj.get("From", "")
                to_port = port_range_obj.get("To", "")
                if from_port == to_port:
                    port_range = str(from_port)
                else:
                    port_range = f"{from_port}-{to_port}"
            else:
                port_range = "All"

            # Get ICMP type/code
            icmp_type_code = entry.get("IcmpTypeCode", {})
            icmp_info = ""
            if icmp_type_code:
                icmp_type = icmp_type_code.get("Type", "")
                icmp_code = icmp_type_code.get("Code", "")
                if icmp_type != "" or icmp_code != "":
                    icmp_info = f"Type: {icmp_type}, Code: {icmp_code}"

            parsed_rules.append({
                "rule_number": rule_number,
                "protocol": self._get_protocol_name(protocol),
                "protocol_number": protocol,
                "rule_action": rule_action,
                "cidr_block": cidr_block,
                "port_range": port_range,
                "icmp_info": icmp_info,
            })

        # Sort by rule number
        parsed_rules.sort(key=lambda x: x["rule_number"])

        return parsed_rules

    @staticmethod
    def _get_protocol_name(protocol: str) -> str:
        """Convert protocol number to name.

        Args:
            protocol: Protocol number

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
        return protocol_map.get(protocol, f"Protocol {protocol}")

    @staticmethod
    def _get_tag_value(tags: list[dict[str, str]], key: str) -> str | None:
        """Extract tag value by key."""
        for tag in tags:
            if tag.get("Key") == key:
                return tag.get("Value")
        return None
