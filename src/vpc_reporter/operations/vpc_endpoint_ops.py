"""VPC Endpoint operations."""

from __future__ import annotations

from typing import Any

from loguru import logger

from vpc_reporter.aws.client import AWSClient


class VPCEndpointOperations:
    """Operations for VPC Endpoint resources."""

    def __init__(self, aws_client: AWSClient) -> None:
        """Initialize VPC endpoint operations.

        Args:
            aws_client: AWS client instance
        """
        self.client = aws_client

    def get_vpc_endpoints(self, vpc_id: str) -> dict[str, Any]:
        """Get all VPC endpoints for a VPC.

        Args:
            vpc_id: VPC ID

        Returns:
            Dictionary with VPC endpoint data
        """
        logger.info(f"Getting VPC endpoints for VPC {vpc_id}")

        response = self.client.describe_vpc_endpoints(
            Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )

        vpc_endpoints = response.get("VpcEndpoints", [])

        processed_endpoints = []
        for endpoint in vpc_endpoints:
            endpoint_type = endpoint.get("VpcEndpointType", "Gateway")

            # Parse security groups (Interface endpoints only)
            security_groups = []
            for sg in endpoint.get("Groups", []):
                security_groups.append(
                    {
                        "group_id": sg.get("GroupId"),
                        "group_name": sg.get("GroupName"),
                    }
                )

            # Parse DNS entries (Interface endpoints only)
            dns_entries = []
            for dns in endpoint.get("DnsEntries", []):
                dns_entries.append(
                    {
                        "dns_name": dns.get("DnsName"),
                        "hosted_zone_id": dns.get("HostedZoneId"),
                    }
                )

            # Extract service name (e.g., "s3" from "com.amazonaws.us-east-1.s3")
            service_name = endpoint.get("ServiceName", "")
            service_short_name = (
                service_name.split(".")[-1] if service_name else "unknown"
            )

            processed_endpoints.append(
                {
                    "vpc_endpoint_id": endpoint["VpcEndpointId"],
                    "vpc_endpoint_type": endpoint_type,
                    "vpc_id": endpoint.get("VpcId"),
                    "service_name": service_name,
                    "service_short_name": service_short_name,
                    "state": endpoint.get("State"),
                    "policy_document": endpoint.get("PolicyDocument"),
                    # Gateway endpoint fields
                    "route_table_ids": endpoint.get("RouteTableIds", []),
                    # Interface endpoint fields
                    "subnet_ids": endpoint.get("SubnetIds", []),
                    "security_groups": security_groups,
                    "network_interface_ids": endpoint.get("NetworkInterfaceIds", []),
                    "dns_entries": dns_entries,
                    "private_dns_enabled": endpoint.get("PrivateDnsEnabled", False),
                    # Common fields
                    "requester_managed": endpoint.get("RequesterManaged", False),
                    "owner_id": endpoint.get("OwnerId"),
                    "creation_timestamp": endpoint.get("CreationTimestamp"),
                    "last_error": endpoint.get("LastError"),
                    "tags": endpoint.get("Tags", []),
                    "name": self._get_tag_value(endpoint.get("Tags", []), "Name"),
                }
            )

        # Count by type
        interface_count = len(
            [e for e in processed_endpoints if e["vpc_endpoint_type"] == "Interface"]
        )
        gateway_count = len(
            [e for e in processed_endpoints if e["vpc_endpoint_type"] == "Gateway"]
        )
        gwlb_count = len(
            [
                e
                for e in processed_endpoints
                if e["vpc_endpoint_type"] == "GatewayLoadBalancer"
            ]
        )

        logger.info(f"Found {len(processed_endpoints)} VPC endpoints")

        return {
            "total_count": len(processed_endpoints),
            "interface_count": interface_count,
            "gateway_count": gateway_count,
            "gateway_load_balancer_count": gwlb_count,
            "vpc_endpoints": processed_endpoints,
            "raw_data": vpc_endpoints,
        }

    @staticmethod
    def _get_tag_value(tags: list[dict[str, str]], key: str) -> str | None:
        """Extract tag value by key."""
        for tag in tags:
            if tag.get("Key") == key:
                return tag.get("Value")
        return None
