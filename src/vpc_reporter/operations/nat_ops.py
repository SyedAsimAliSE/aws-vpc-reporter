"""NAT Gateway operations."""

from __future__ import annotations

from typing import Any

from loguru import logger

from vpc_reporter.aws.client import AWSClient


class NATGatewayOperations:
    """Operations for NAT Gateway resources."""

    def __init__(self, aws_client: AWSClient) -> None:
        """Initialize NAT gateway operations.

        Args:
            aws_client: AWS client instance
        """
        self.client = aws_client

    def get_nat_gateways(self, vpc_id: str) -> dict[str, Any]:
        """Get all NAT gateways for a VPC.

        Args:
            vpc_id: VPC ID

        Returns:
            Dictionary with NAT gateway data
        """
        logger.info(f"Getting NAT gateways for VPC {vpc_id}")

        response = self.client.describe_nat_gateways(
            Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )

        nat_gateways = response.get("NatGateways", [])

        processed_nats = []
        for nat in nat_gateways:
            # Parse NAT gateway addresses (CRITICAL for EIP info)
            addresses = []
            for addr in nat.get("NatGatewayAddresses", []):
                addresses.append({
                    "allocation_id": addr.get("AllocationId"),
                    "network_interface_id": addr.get("NetworkInterfaceId"),
                    "private_ip": addr.get("PrivateIp"),
                    "public_ip": addr.get("PublicIp"),
                    "association_id": addr.get("AssociationId"),
                    "is_primary": addr.get("IsPrimary", False),
                    "failure_message": addr.get("FailureMessage"),
                    "status": addr.get("Status"),
                })

            # Extract primary public IP for easy access
            primary_public_ip = None
            for addr in addresses:
                if addr["is_primary"] and addr["public_ip"]:
                    primary_public_ip = addr["public_ip"]
                    break

            processed_nats.append({
                "nat_gateway_id": nat["NatGatewayId"],
                "subnet_id": nat.get("SubnetId"),
                "vpc_id": nat.get("VpcId"),
                "state": nat.get("State"),
                "create_time": nat.get("CreateTime"),
                "delete_time": nat.get("DeleteTime"),
                "failure_code": nat.get("FailureCode"),
                "failure_message": nat.get("FailureMessage"),
                "connectivity_type": nat.get("ConnectivityType", "public"),
                "nat_gateway_addresses": addresses,
                "primary_public_ip": primary_public_ip,
                "address_count": len(addresses),
                "tags": nat.get("Tags", []),
                "name": self._get_tag_value(nat.get("Tags", []), "Name"),
            })

        logger.info(f"Found {len(processed_nats)} NAT gateways")

        return {
            "total_count": len(processed_nats),
            "nat_gateways": processed_nats,
            "raw_data": nat_gateways,
        }

    @staticmethod
    def _get_tag_value(tags: list[dict[str, str]], key: str) -> str | None:
        """Extract tag value by key."""
        for tag in tags:
            if tag.get("Key") == key:
                return tag.get("Value")
        return None
