"""DHCP Options operations."""

from __future__ import annotations

from typing import Any

from loguru import logger

from vpc_reporter.aws.client import AWSClient


class DHCPOptionsOperations:
    """Operations for DHCP Options Set resources."""

    def __init__(self, aws_client: AWSClient) -> None:
        """Initialize DHCP options operations.

        Args:
            aws_client: AWS client instance
        """
        self.client = aws_client

    def get_dhcp_options(self, dhcp_options_id: str) -> dict[str, Any]:
        """Get DHCP options set details.

        Args:
            dhcp_options_id: DHCP Options Set ID from VPC

        Returns:
            Dictionary with DHCP options data
        """
        logger.info(f"Getting DHCP options for {dhcp_options_id}")

        if not dhcp_options_id:
            return {
                "dhcp_options_id": None,
                "configurations": {},
                "raw_data": None,
            }

        response = self.client.describe_dhcp_options(
            DhcpOptionsIds=[dhcp_options_id]
        )

        dhcp_options_list = response.get("DhcpOptions", [])

        if not dhcp_options_list:
            return {
                "dhcp_options_id": dhcp_options_id,
                "configurations": {},
                "raw_data": None,
            }

        dhcp_options = dhcp_options_list[0]

        # Parse DHCP configurations
        configurations = {}
        for config in dhcp_options.get("DhcpConfigurations", []):
            key = config.get("Key")
            values = [v.get("Value") for v in config.get("Values", [])]
            configurations[key] = values

        result = {
            "dhcp_options_id": dhcp_options["DhcpOptionsId"],
            "owner_id": dhcp_options.get("OwnerId"),
            "configurations": configurations,
            "domain_name": configurations.get("domain-name", []),
            "domain_name_servers": configurations.get("domain-name-servers", []),
            "ntp_servers": configurations.get("ntp-servers", []),
            "netbios_name_servers": configurations.get("netbios-name-servers", []),
            "netbios_node_type": configurations.get("netbios-node-type", []),
            "tags": dhcp_options.get("Tags", []),
            "name": self._get_tag_value(dhcp_options.get("Tags", []), "Name"),
            "raw_data": dhcp_options,
        }

        logger.info(f"Retrieved DHCP options {dhcp_options_id}")

        return result

    @staticmethod
    def _get_tag_value(tags: list[dict[str, str]], key: str) -> str | None:
        """Extract tag value by key."""
        for tag in tags:
            if tag.get("Key") == key:
                return tag.get("Value")
        return None
