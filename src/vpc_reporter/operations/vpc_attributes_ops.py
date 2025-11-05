"""VPC Attributes operations."""

from __future__ import annotations

from typing import Any

from loguru import logger

from vpc_reporter.aws.client import AWSClient


class VPCAttributesOperations:
    """Operations for VPC Attributes."""

    def __init__(self, aws_client: AWSClient) -> None:
        """Initialize VPC attributes operations.

        Args:
            aws_client: AWS client instance
        """
        self.client = aws_client

    def get_vpc_attributes(self, vpc_id: str) -> dict[str, Any]:
        """Get VPC attributes (DNS settings).

        Note: Requires separate API calls for each attribute.

        Args:
            vpc_id: VPC ID

        Returns:
            Dictionary with VPC attributes
        """
        logger.info(f"Getting VPC attributes for {vpc_id}")

        attributes = {}

        # Get enableDnsSupport
        try:
            response = self.client.describe_vpc_attribute(
                VpcId=vpc_id, Attribute="enableDnsSupport"
            )
            attributes["enable_dns_support"] = response.get("EnableDnsSupport", {}).get(
                "Value", False
            )
        except Exception as e:
            logger.warning(f"Failed to get enableDnsSupport: {e}")
            attributes["enable_dns_support"] = None

        # Get enableDnsHostnames
        try:
            response = self.client.describe_vpc_attribute(
                VpcId=vpc_id, Attribute="enableDnsHostnames"
            )
            attributes["enable_dns_hostnames"] = response.get(
                "EnableDnsHostnames", {}
            ).get("Value", False)
        except Exception as e:
            logger.warning(f"Failed to get enableDnsHostnames: {e}")
            attributes["enable_dns_hostnames"] = None

        # Get enableNetworkAddressUsageMetrics
        try:
            response = self.client.describe_vpc_attribute(
                VpcId=vpc_id, Attribute="enableNetworkAddressUsageMetrics"
            )
            attributes["enable_network_address_usage_metrics"] = response.get(
                "EnableNetworkAddressUsageMetrics", {}
            ).get("Value", False)
        except Exception as e:
            logger.warning(f"Failed to get enableNetworkAddressUsageMetrics: {e}")
            attributes["enable_network_address_usage_metrics"] = None

        logger.info(f"Retrieved VPC attributes for {vpc_id}")

        return {
            "vpc_id": vpc_id,
            "attributes": attributes,
        }
