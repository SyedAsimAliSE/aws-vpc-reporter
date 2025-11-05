"""Customer Gateway operations."""

from __future__ import annotations

from typing import Any

from loguru import logger

from vpc_reporter.aws.client import AWSClient


class CustomerGatewayOperations:
    """Operations for Customer Gateway resources."""

    def __init__(self, aws_client: AWSClient) -> None:
        """Initialize customer gateway operations.

        Args:
            aws_client: AWS client instance
        """
        self.client = aws_client

    def get_customer_gateways(self) -> dict[str, Any]:
        """Get all customer gateways in the region.

        Note: Customer gateways are not VPC-specific, so we get all in the region.

        Returns:
            Dictionary with customer gateway data
        """
        logger.info("Getting customer gateways")

        response = self.client.describe_customer_gateways()

        customer_gateways = response.get("CustomerGateways", [])

        processed_cgws = []
        for cgw in customer_gateways:
            processed_cgws.append({
                "customer_gateway_id": cgw["CustomerGatewayId"],
                "state": cgw.get("State"),
                "type": cgw.get("Type", "ipsec.1"),
                "ip_address": cgw.get("IpAddress"),
                "bgp_asn": cgw.get("BgpAsn"),
                "device_name": cgw.get("DeviceName"),
                "certificate_arn": cgw.get("CertificateArn"),
                "tags": cgw.get("Tags", []),
                "name": self._get_tag_value(cgw.get("Tags", []), "Name"),
            })

        logger.info(f"Found {len(processed_cgws)} customer gateways")

        return {
            "total_count": len(processed_cgws),
            "customer_gateways": processed_cgws,
            "raw_data": customer_gateways,
        }

    @staticmethod
    def _get_tag_value(tags: list[dict[str, str]], key: str) -> str | None:
        """Extract tag value by key."""
        for tag in tags:
            if tag.get("Key") == key:
                return tag.get("Value")
        return None
