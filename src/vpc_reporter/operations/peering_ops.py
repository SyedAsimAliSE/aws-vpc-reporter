"""VPC Peering operations."""

from __future__ import annotations

from typing import Any

from loguru import logger

from vpc_reporter.aws.client import AWSClient


class VPCPeeringOperations:
    """Operations for VPC Peering Connection resources."""

    def __init__(self, aws_client: AWSClient) -> None:
        """Initialize VPC peering operations.

        Args:
            aws_client: AWS client instance
        """
        self.client = aws_client

    def get_vpc_peering_connections(self, vpc_id: str) -> dict[str, Any]:
        """Get all VPC peering connections for a VPC.

        Args:
            vpc_id: VPC ID

        Returns:
            Dictionary with VPC peering connection data
        """
        logger.info(f"Getting VPC peering connections for VPC {vpc_id}")

        # Get peering connections where this VPC is either requester or accepter
        response = self.client.describe_vpc_peering_connections(
            Filters=[
                {"Name": "requester-vpc-info.vpc-id", "Values": [vpc_id]},
            ]
        )

        peering_as_requester = response.get("VpcPeeringConnections", [])

        response2 = self.client.describe_vpc_peering_connections(
            Filters=[
                {"Name": "accepter-vpc-info.vpc-id", "Values": [vpc_id]},
            ]
        )

        peering_as_accepter = response2.get("VpcPeeringConnections", [])

        # Combine and deduplicate
        all_peering = {p["VpcPeeringConnectionId"]: p for p in peering_as_requester}
        all_peering.update(
            {p["VpcPeeringConnectionId"]: p for p in peering_as_accepter}
        )
        peering_connections = list(all_peering.values())

        processed_peering = []
        for peering in peering_connections:
            # Parse requester VPC info
            requester_info = peering.get("RequesterVpcInfo", {})
            requester_vpc = {
                "vpc_id": requester_info.get("VpcId"),
                "owner_id": requester_info.get("OwnerId"),
                "cidr_block": requester_info.get("CidrBlock"),
                "region": requester_info.get("Region"),
                "ipv6_cidr_blocks": [
                    block.get("Ipv6CidrBlock")
                    for block in requester_info.get("Ipv6CidrBlockSet", [])
                ],
                "cidr_blocks": [
                    block.get("CidrBlock")
                    for block in requester_info.get("CidrBlockSet", [])
                ],
            }

            # Parse accepter VPC info
            accepter_info = peering.get("AccepterVpcInfo", {})
            accepter_vpc = {
                "vpc_id": accepter_info.get("VpcId"),
                "owner_id": accepter_info.get("OwnerId"),
                "cidr_block": accepter_info.get("CidrBlock"),
                "region": accepter_info.get("Region"),
                "ipv6_cidr_blocks": [
                    block.get("Ipv6CidrBlock")
                    for block in accepter_info.get("Ipv6CidrBlockSet", [])
                ],
                "cidr_blocks": [
                    block.get("CidrBlock")
                    for block in accepter_info.get("CidrBlockSet", [])
                ],
            }

            # Determine if cross-account or cross-region
            is_cross_account = requester_vpc["owner_id"] != accepter_vpc["owner_id"]
            is_cross_region = requester_vpc["region"] != accepter_vpc["region"]

            # Determine role (requester or accepter)
            role = "requester" if requester_vpc["vpc_id"] == vpc_id else "accepter"
            peer_vpc = accepter_vpc if role == "requester" else requester_vpc

            # Parse status
            status = peering.get("Status", {})

            processed_peering.append(
                {
                    "vpc_peering_connection_id": peering["VpcPeeringConnectionId"],
                    "status_code": status.get("Code"),
                    "status_message": status.get("Message"),
                    "expiration_time": peering.get("ExpirationTime"),
                    "requester_vpc": requester_vpc,
                    "accepter_vpc": accepter_vpc,
                    "role": role,
                    "peer_vpc": peer_vpc,
                    "is_cross_account": is_cross_account,
                    "is_cross_region": is_cross_region,
                    "tags": peering.get("Tags", []),
                    "name": self._get_tag_value(peering.get("Tags", []), "Name"),
                }
            )

        logger.info(f"Found {len(processed_peering)} VPC peering connections")

        return {
            "total_count": len(processed_peering),
            "cross_account_count": len(
                [p for p in processed_peering if p["is_cross_account"]]
            ),
            "cross_region_count": len(
                [p for p in processed_peering if p["is_cross_region"]]
            ),
            "peering_connections": processed_peering,
            "raw_data": peering_connections,
        }

    @staticmethod
    def _get_tag_value(tags: list[dict[str, str]], key: str) -> str | None:
        """Extract tag value by key."""
        for tag in tags:
            if tag.get("Key") == key:
                return tag.get("Value")
        return None
