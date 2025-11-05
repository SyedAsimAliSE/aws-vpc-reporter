"""Network Interface (ENI) operations."""

from __future__ import annotations

from typing import Any

from loguru import logger

from vpc_reporter.aws.client import AWSClient


class NetworkInterfaceOperations:
    """Operations for Network Interface (ENI) resources."""

    def __init__(self, aws_client: AWSClient) -> None:
        """Initialize network interface operations.

        Args:
            aws_client: AWS client instance
        """
        self.client = aws_client

    def get_network_interfaces(self, vpc_id: str) -> dict[str, Any]:
        """Get all network interfaces for a VPC.

        Args:
            vpc_id: VPC ID

        Returns:
            Dictionary with network interface data
        """
        logger.info(f"Getting network interfaces for VPC {vpc_id}")

        response = self.client.describe_network_interfaces(
            Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )

        network_interfaces = response.get("NetworkInterfaces", [])

        processed_enis = []
        for eni in network_interfaces:
            # Parse security groups
            security_groups = []
            for sg in eni.get("Groups", []):
                security_groups.append(
                    {
                        "group_id": sg.get("GroupId"),
                        "group_name": sg.get("GroupName"),
                    }
                )

            # **CRITICAL**: Parse attachment (shows what it's attached to)
            attachment = eni.get("Attachment", {})
            attachment_info = (
                {
                    "attachment_id": attachment.get("AttachmentId"),
                    "instance_id": attachment.get("InstanceId"),
                    "instance_owner_id": attachment.get("InstanceOwnerId"),
                    "device_index": attachment.get("DeviceIndex"),
                    "status": attachment.get("Status"),
                    "attach_time": attachment.get("AttachTime"),
                    "delete_on_termination": attachment.get(
                        "DeleteOnTermination", False
                    ),
                    "network_card_index": attachment.get("NetworkCardIndex"),
                }
                if attachment
                else None
            )

            # Parse association (public IP)
            association = eni.get("Association", {})
            association_info = (
                {
                    "public_ip": association.get("PublicIp"),
                    "public_dns_name": association.get("PublicDnsName"),
                    "allocation_id": association.get("AllocationId"),
                    "association_id": association.get("AssociationId"),
                    "ip_owner_id": association.get("IpOwnerId"),
                    "carrier_ip": association.get("CarrierIp"),
                }
                if association
                else None
            )

            # Parse all private IP addresses (primary + secondary)
            private_ips = []
            for ip in eni.get("PrivateIpAddresses", []):
                ip_association = ip.get("Association", {})
                private_ips.append(
                    {
                        "private_ip_address": ip.get("PrivateIpAddress"),
                        "private_dns_name": ip.get("PrivateDnsName"),
                        "primary": ip.get("Primary", False),
                        "association": (
                            {
                                "public_ip": ip_association.get("PublicIp"),
                                "public_dns_name": ip_association.get("PublicDnsName"),
                                "allocation_id": ip_association.get("AllocationId"),
                                "association_id": ip_association.get("AssociationId"),
                                "ip_owner_id": ip_association.get("IpOwnerId"),
                                "carrier_ip": ip_association.get("CarrierIp"),
                            }
                            if ip_association
                            else None
                        ),
                    }
                )

            # Parse IPv6 addresses
            ipv6_addresses = []
            for ipv6 in eni.get("Ipv6Addresses", []):
                ipv6_addresses.append(
                    {
                        "ipv6_address": ipv6.get("Ipv6Address"),
                        "is_primary_ipv6": ipv6.get("IsPrimaryIpv6", False),
                    }
                )

            # Parse IPv4 prefixes
            ipv4_prefixes = [
                prefix.get("Ipv4Prefix") for prefix in eni.get("Ipv4Prefixes", [])
            ]

            # Parse IPv6 prefixes
            ipv6_prefixes = [
                prefix.get("Ipv6Prefix") for prefix in eni.get("Ipv6Prefixes", [])
            ]

            # **CRITICAL**: Interface type (identifies AWS-managed ENIs)
            interface_type = eni.get("InterfaceType", "interface")

            # Determine if AWS-managed
            requester_managed = eni.get("RequesterManaged", False)
            requester_id = eni.get("RequesterId")

            # Friendly description of what owns this ENI
            owner_description = self._get_owner_description(
                interface_type, requester_managed, requester_id, attachment_info
            )

            processed_enis.append(
                {
                    "network_interface_id": eni["NetworkInterfaceId"],
                    "subnet_id": eni.get("SubnetId"),
                    "vpc_id": eni.get("VpcId"),
                    "availability_zone": eni.get("AvailabilityZone"),
                    "availability_zone_id": eni.get("AvailabilityZoneId"),
                    "description": eni.get("Description"),
                    "owner_id": eni.get("OwnerId"),
                    "requester_id": requester_id,
                    "requester_managed": requester_managed,
                    "status": eni.get("Status"),
                    # **CRITICAL**: Interface type
                    "interface_type": interface_type,
                    "owner_description": owner_description,
                    # Network details
                    "mac_address": eni.get("MacAddress"),
                    "private_ip_address": eni.get("PrivateIpAddress"),
                    "private_dns_name": eni.get("PrivateDnsName"),
                    "source_dest_check": eni.get("SourceDestCheck", True),
                    # Security
                    "security_groups": security_groups,
                    "security_group_count": len(security_groups),
                    # **CRITICAL**: Attachment details
                    "attachment": attachment_info,
                    "attached_to": (
                        attachment_info.get("instance_id") if attachment_info else None
                    ),
                    "is_attached": bool(attachment_info),
                    # Public IP association
                    "association": association_info,
                    "has_public_ip": bool(
                        association_info and association_info.get("public_ip")
                    ),
                    "public_ip": (
                        association_info.get("public_ip") if association_info else None
                    ),
                    # IP addresses
                    "private_ip_addresses": private_ips,
                    "private_ip_count": len(private_ips),
                    "ipv6_addresses": ipv6_addresses,
                    "ipv6_address_count": len(ipv6_addresses),
                    "ipv4_prefixes": ipv4_prefixes,
                    "ipv6_prefixes": ipv6_prefixes,
                    # Additional flags
                    "ipv6_native": eni.get("Ipv6Native", False),
                    "outpost_arn": eni.get("OutpostArn"),
                    "deny_all_igw_traffic": eni.get("DenyAllIgwTraffic", False),
                    "ipv6_share_policy": eni.get("Ipv6SharePolicy"),
                    # Metadata
                    "tags": eni.get("TagSet", []),
                    "name": self._get_tag_value(eni.get("TagSet", []), "Name"),
                }
            )

        # Count by interface type
        type_counts: dict[str, int] = {}
        for eni in processed_enis:
            itype = eni["interface_type"]
            type_counts[itype] = type_counts.get(itype, 0) + 1

        logger.info(f"Found {len(processed_enis)} network interfaces")

        return {
            "total_count": len(processed_enis),
            "interface_type_counts": type_counts,
            "aws_managed_count": len(
                [e for e in processed_enis if e["requester_managed"]]
            ),
            "user_managed_count": len(
                [e for e in processed_enis if not e["requester_managed"]]
            ),
            "network_interfaces": processed_enis,
            "raw_data": network_interfaces,
        }

    @staticmethod
    def _get_owner_description(
        interface_type: str,
        requester_managed: bool,
        requester_id: str | None,
        attachment_info: dict[str, Any] | None,
    ) -> str:
        """Get friendly description of what owns this ENI."""
        if interface_type == "nat_gateway":
            return "NAT Gateway"
        elif interface_type == "vpc_endpoint":
            return "VPC Endpoint"
        elif interface_type == "lambda":
            return "Lambda Function"
        elif interface_type == "network_load_balancer":
            return "Network Load Balancer"
        elif interface_type == "gateway_load_balancer":
            return "Gateway Load Balancer"
        elif interface_type == "gateway_load_balancer_endpoint":
            return "Gateway Load Balancer Endpoint"
        elif interface_type == "transit_gateway":
            return "Transit Gateway"
        elif interface_type == "efs":
            return "EFS Mount Target"
        elif interface_type == "efa":
            return "Elastic Fabric Adapter"
        elif interface_type == "load_balancer":
            return "Classic Load Balancer"
        elif interface_type == "quicksight":
            return "QuickSight"
        elif interface_type == "global_accelerator_managed":
            return "Global Accelerator"
        elif interface_type == "api_gateway_managed":
            return "API Gateway"
        elif interface_type == "aws_codestar_connections_managed":
            return "CodeStar Connections"
        elif interface_type == "iot_rules_managed":
            return "IoT Rules"
        elif interface_type == "ec2_instance_connect_endpoint":
            return "EC2 Instance Connect Endpoint"
        elif interface_type == "trunk":
            return "Trunk ENI"
        elif interface_type == "branch":
            return "Branch ENI"
        elif interface_type == "evs":
            return "Elastic Volume Service"
        elif requester_managed and requester_id:
            return f"AWS Service ({requester_id})"
        elif attachment_info and attachment_info.get("instance_id"):
            return f"EC2 Instance ({attachment_info['instance_id']})"
        elif interface_type == "interface":
            return "Standard ENI"
        else:
            return f"Unknown ({interface_type})"

    @staticmethod
    def _get_tag_value(tags: list[dict[str, str]], key: str) -> str | None:
        """Extract tag value by key."""
        for tag in tags:
            if tag.get("Key") == key:
                return tag.get("Value")
        return None
