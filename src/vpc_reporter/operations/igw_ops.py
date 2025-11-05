"""Internet Gateway operations."""

from __future__ import annotations

from typing import Any

from loguru import logger

from vpc_reporter.aws.client import AWSClient


class InternetGatewayOperations:
    """Operations for Internet Gateway resources."""

    def __init__(self, aws_client: AWSClient) -> None:
        """Initialize internet gateway operations.

        Args:
            aws_client: AWS client instance
        """
        self.client = aws_client

    def get_internet_gateways(self, vpc_id: str) -> dict[str, Any]:
        """Get all internet gateways for a VPC.

        Args:
            vpc_id: VPC ID

        Returns:
            Dictionary with internet gateway data
        """
        logger.info(f"Getting internet gateways for VPC {vpc_id}")

        response = self.client.describe_internet_gateways(
            Filters=[{"Name": "attachment.vpc-id", "Values": [vpc_id]}]
        )

        igws = response.get("InternetGateways", [])

        processed_igws = []
        for igw in igws:
            # Parse attachments
            attachments = []
            for attachment in igw.get("Attachments", []):
                attachments.append({
                    "vpc_id": attachment.get("VpcId"),
                    "state": attachment.get("State"),
                })

            processed_igws.append({
                "internet_gateway_id": igw["InternetGatewayId"],
                "owner_id": igw.get("OwnerId"),
                "attachments": attachments,
                "attached_vpc_id": attachments[0]["vpc_id"] if attachments else None,
                "attachment_state": attachments[0]["state"] if attachments else None,
                "tags": igw.get("Tags", []),
                "name": self._get_tag_value(igw.get("Tags", []), "Name"),
            })

        logger.info(f"Found {len(processed_igws)} internet gateways")

        return {
            "total_count": len(processed_igws),
            "internet_gateways": processed_igws,
            "raw_data": igws,
        }

    @staticmethod
    def _get_tag_value(tags: list[dict[str, str]], key: str) -> str | None:
        """Extract tag value by key."""
        for tag in tags:
            if tag.get("Key") == key:
                return tag.get("Value")
        return None
