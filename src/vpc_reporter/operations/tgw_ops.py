"""Transit Gateway VPC Attachment operations."""

from __future__ import annotations

from typing import Any

from loguru import logger

from vpc_reporter.aws.client import AWSClient


class TransitGatewayAttachmentOperations:
    """Operations for Transit Gateway VPC Attachment resources."""

    def __init__(self, aws_client: AWSClient) -> None:
        """Initialize Transit Gateway attachment operations.

        Args:
            aws_client: AWS client instance
        """
        self.client = aws_client

    def get_transit_gateway_attachments(self, vpc_id: str) -> dict[str, Any]:
        """Get all Transit Gateway VPC attachments for a VPC.

        Args:
            vpc_id: VPC ID

        Returns:
            Dictionary with Transit Gateway attachment data
        """
        logger.info(f"Getting Transit Gateway attachments for VPC {vpc_id}")

        response = self.client.describe_transit_gateway_vpc_attachments(
            Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )

        attachments = response.get("TransitGatewayVpcAttachments", [])

        processed_attachments = []
        for attachment in attachments:
            # Parse options
            options = attachment.get("Options", {})

            processed_attachments.append({
                "transit_gateway_attachment_id": attachment["TransitGatewayAttachmentId"],
                "transit_gateway_id": attachment.get("TransitGatewayId"),
                "vpc_id": attachment.get("VpcId"),
                "vpc_owner_id": attachment.get("VpcOwnerId"),
                "state": attachment.get("State"),
                "subnet_ids": attachment.get("SubnetIds", []),
                "subnet_count": len(attachment.get("SubnetIds", [])),
                "creation_time": attachment.get("CreationTime"),
                # Options
                "dns_support": options.get("DnsSupport", "enable"),
                "security_group_referencing_support": options.get("SecurityGroupReferencingSupport", "enable"),
                "ipv6_support": options.get("Ipv6Support", "disable"),
                "appliance_mode_support": options.get("ApplianceModeSupport", "disable"),
                "tags": attachment.get("Tags", []),
                "name": self._get_tag_value(attachment.get("Tags", []), "Name"),
            })

        logger.info(f"Found {len(processed_attachments)} Transit Gateway attachments")

        return {
            "total_count": len(processed_attachments),
            "attachments": processed_attachments,
            "raw_data": attachments,
        }

    @staticmethod
    def _get_tag_value(tags: list[dict[str, str]], key: str) -> str | None:
        """Extract tag value by key."""
        for tag in tags:
            if tag.get("Key") == key:
                return tag.get("Value")
        return None
