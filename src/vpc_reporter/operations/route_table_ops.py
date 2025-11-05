"""Route table operations."""

from __future__ import annotations

from typing import Any

from loguru import logger

from vpc_reporter.aws.client import AWSClient


class RouteTableOperations:
    """Operations for Route Table resources."""

    def __init__(self, aws_client: AWSClient) -> None:
        """Initialize route table operations.

        Args:
            aws_client: AWS client instance
        """
        self.client = aws_client

    def get_route_tables(self, vpc_id: str) -> dict[str, Any]:
        """Get all route tables for a VPC.

        Args:
            vpc_id: VPC ID

        Returns:
            Dictionary with route table data
        """
        logger.info(f"Getting route tables for VPC {vpc_id}")

        response = self.client.describe_route_tables(
            Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )

        route_tables = response.get("RouteTables", [])

        processed_tables = []
        for rt in route_tables:
            # Check if main route table
            is_main = any(
                assoc.get("Main", False) for assoc in rt.get("Associations", [])
            )

            # Get associated subnets
            associated_subnets = [
                assoc.get("SubnetId")
                for assoc in rt.get("Associations", [])
                if assoc.get("SubnetId")
            ]

            # Process routes with all target types
            routes = []
            for route in rt.get("Routes", []):
                # Determine target type and value
                target_type = "Unknown"
                target_value = "N/A"

                if route.get("GatewayId"):
                    target_type = "Gateway"
                    target_value = route.get("GatewayId")
                elif route.get("NatGatewayId"):
                    target_type = "NAT Gateway"
                    target_value = route.get("NatGatewayId")
                elif route.get("TransitGatewayId"):
                    target_type = "Transit Gateway"
                    target_value = route.get("TransitGatewayId")
                elif route.get("VpcPeeringConnectionId"):
                    target_type = "VPC Peering"
                    target_value = route.get("VpcPeeringConnectionId")
                elif route.get("NetworkInterfaceId"):
                    target_type = "Network Interface"
                    target_value = route.get("NetworkInterfaceId")
                elif route.get("InstanceId"):
                    target_type = "Instance"
                    target_value = route.get("InstanceId")
                elif route.get("LocalGatewayId"):
                    target_type = "Local Gateway"
                    target_value = route.get("LocalGatewayId")
                elif route.get("CarrierGatewayId"):
                    target_type = "Carrier Gateway"
                    target_value = route.get("CarrierGatewayId")
                elif route.get("EgressOnlyInternetGatewayId"):
                    target_type = "Egress-Only IGW"
                    target_value = route.get("EgressOnlyInternetGatewayId")
                elif route.get("CoreNetworkArn"):
                    target_type = "Core Network"
                    target_value = route.get("CoreNetworkArn")

                routes.append(
                    {
                        "destination": (
                            route.get("DestinationCidrBlock")
                            or route.get("DestinationIpv6CidrBlock")
                            or route.get("DestinationPrefixListId")
                            or "N/A"
                        ),
                        "target": target_value,
                        "target_type": target_type,
                        "state": route.get("State", "unknown"),
                        "origin": route.get("Origin", "unknown"),
                    }
                )

            # Get propagating VGWs
            propagating_vgws = [
                vgw.get("GatewayId") for vgw in rt.get("PropagatingVgws", [])
            ]

            # Parse associations with full details
            associations_detail = []
            for assoc in rt.get("Associations", []):
                associations_detail.append(
                    {
                        "route_table_association_id": assoc.get(
                            "RouteTableAssociationId"
                        ),
                        "subnet_id": assoc.get("SubnetId"),
                        "gateway_id": assoc.get("GatewayId"),
                        "main": assoc.get("Main", False),
                        "association_state": assoc.get("AssociationState", {}).get(
                            "State"
                        ),
                    }
                )

            processed_tables.append(
                {
                    "route_table_id": rt["RouteTableId"],
                    "vpc_id": rt.get("VpcId"),
                    "owner_id": rt.get("OwnerId"),
                    "is_main": is_main,
                    "associated_subnets": associated_subnets,
                    "associations": associations_detail,
                    "routes": routes,
                    "propagating_vgws": propagating_vgws,
                    "name": self._get_tag_value(rt.get("Tags", []), "Name"),
                    "tags": rt.get("Tags", []),
                }
            )

        logger.info(f"Found {len(processed_tables)} route tables")

        return {
            "total_count": len(processed_tables),
            "route_tables": processed_tables,
            "raw_data": route_tables,
        }

    @staticmethod
    def _get_tag_value(tags: list[dict[str, str]], key: str) -> str | None:
        """Extract tag value by key."""
        for tag in tags:
            if tag.get("Key") == key:
                return tag.get("Value")
        return None
