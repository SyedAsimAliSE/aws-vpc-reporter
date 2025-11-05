"""Integration test for all 19 VPC sections.

This test verifies that all sections can be collected and formatted without errors.
It uses mocked AWS responses to avoid actual AWS API calls.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from rich.console import Console

from vpc_reporter.aws.client import AWSClient
from vpc_reporter.operations.sync_collector import collect_all_data_sync
from vpc_reporter.output.console import render_console_output
from vpc_reporter.output.markdown import generate_markdown


@pytest.fixture
def mock_aws_client() -> AWSClient:
    """Create a mock AWS client with all required methods."""
    client = MagicMock(spec=AWSClient)
    client.region = "us-east-1"
    client.profile = "test-profile"

    # Mock all AWS API responses
    client.describe_vpcs.return_value = {
        "Vpcs": [{
            "VpcId": "vpc-test123",
            "CidrBlock": "10.0.0.0/16",
            "State": "available",
            "Tags": [{"Key": "Name", "Value": "Test VPC"}],
            "InstanceTenancy": "default",
            "IsDefault": False,
            "DhcpOptionsId": "dopt-test123",
        }]
    }

    client.describe_vpc_attribute.return_value = {
        "EnableDnsSupport": {"Value": True},
        "EnableDnsHostnames": {"Value": True},
    }

    client.describe_subnets.return_value = {
        "Subnets": [{
            "SubnetId": "subnet-test123",
            "VpcId": "vpc-test123",
            "CidrBlock": "10.0.1.0/24",
            "AvailabilityZone": "us-east-1a",
            "AvailableIpAddressCount": 251,
            "State": "available",
            "MapPublicIpOnLaunch": True,
            "Tags": [{"Key": "Name", "Value": "Test Subnet"}],
        }]
    }

    client.describe_route_tables.return_value = {
        "RouteTables": [{
            "RouteTableId": "rtb-test123",
            "VpcId": "vpc-test123",
            "Routes": [
                {
                    "DestinationCidrBlock": "10.0.0.0/16",
                    "GatewayId": "local",
                    "State": "active",
                },
                {
                    "DestinationCidrBlock": "0.0.0.0/0",
                    "GatewayId": "igw-test123",
                    "State": "active",
                }
            ],
            "Associations": [{
                "RouteTableAssociationId": "rtbassoc-test123",
                "SubnetId": "subnet-test123",
                "Main": False,
            }],
            "Tags": [{"Key": "Name", "Value": "Test Route Table"}],
        }]
    }

    client.describe_security_groups.return_value = {
        "SecurityGroups": [{
            "GroupId": "sg-test123",
            "GroupName": "test-sg",
            "Description": "Test security group",
            "VpcId": "vpc-test123",
            "IpPermissions": [{
                "IpProtocol": "tcp",
                "FromPort": 443,
                "ToPort": 443,
                "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
            }],
            "IpPermissionsEgress": [{
                "IpProtocol": "-1",
                "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
            }],
            "Tags": [{"Key": "Name", "Value": "Test SG"}],
        }]
    }

    client.describe_network_acls.return_value = {
        "NetworkAcls": [{
            "NetworkAclId": "acl-test123",
            "VpcId": "vpc-test123",
            "IsDefault": True,
            "Entries": [
                {
                    "RuleNumber": 100,
                    "Protocol": "-1",
                    "RuleAction": "allow",
                    "Egress": False,
                    "CidrBlock": "0.0.0.0/0",
                },
                {
                    "RuleNumber": 100,
                    "Protocol": "-1",
                    "RuleAction": "allow",
                    "Egress": True,
                    "CidrBlock": "0.0.0.0/0",
                }
            ],
            "Associations": [{
                "NetworkAclAssociationId": "aclassoc-test123",
                "SubnetId": "subnet-test123",
            }],
            "Tags": [{"Key": "Name", "Value": "Test NACL"}],
        }]
    }

    client.describe_internet_gateways.return_value = {
        "InternetGateways": [{
            "InternetGatewayId": "igw-test123",
            "Attachments": [{
                "VpcId": "vpc-test123",
                "State": "available",
            }],
            "Tags": [{"Key": "Name", "Value": "Test IGW"}],
        }]
    }

    client.describe_nat_gateways.return_value = {
        "NatGateways": [{
            "NatGatewayId": "nat-test123",
            "SubnetId": "subnet-test123",
            "VpcId": "vpc-test123",
            "State": "available",
            "NatGatewayAddresses": [{
                "PublicIp": "54.1.2.3",
                "PrivateIp": "10.0.1.5",
            }],
            "Tags": [{"Key": "Name", "Value": "Test NAT"}],
        }]
    }

    client.describe_addresses.return_value = {
        "Addresses": [{
            "PublicIp": "54.1.2.3",
            "AllocationId": "eipalloc-test123",
            "Domain": "vpc",
            "NetworkInterfaceId": "eni-test123",
            "AssociationId": "eipassoc-test123",
            "Tags": [{"Key": "Name", "Value": "Test EIP"}],
        }]
    }

    client.describe_vpc_endpoints.return_value = {
        "VpcEndpoints": [{
            "VpcEndpointId": "vpce-test123",
            "VpcId": "vpc-test123",
            "ServiceName": "com.amazonaws.us-east-1.s3",
            "VpcEndpointType": "Gateway",
            "State": "available",
            "RouteTableIds": ["rtb-test123"],
            "Tags": [{"Key": "Name", "Value": "Test Endpoint"}],
        }]
    }

    client.describe_vpc_peering_connections.return_value = {
        "VpcPeeringConnections": [{
            "VpcPeeringConnectionId": "pcx-test123",
            "RequesterVpcInfo": {"VpcId": "vpc-test123"},
            "AccepterVpcInfo": {"VpcId": "vpc-test456"},
            "Status": {"Code": "active"},
            "Tags": [{"Key": "Name", "Value": "Test Peering"}],
        }]
    }

    client.describe_transit_gateway_vpc_attachments.return_value = {
        "TransitGatewayVpcAttachments": [{
            "TransitGatewayAttachmentId": "tgw-attach-test123",
            "TransitGatewayId": "tgw-test123",
            "VpcId": "vpc-test123",
            "State": "available",
            "Options": {
                "DnsSupport": "enable",
                "Ipv6Support": "disable",
            },
            "Tags": [{"Key": "Name", "Value": "Test TGW Attachment"}],
        }]
    }

    client.describe_vpn_connections.return_value = {
        "VpnConnections": [{
            "VpnConnectionId": "vpn-test123",
            "State": "available",
            "Type": "ipsec.1",
            "CustomerGatewayId": "cgw-test123",
            "VpnGatewayId": "vgw-test123",
            "Options": {
                "StaticRoutesOnly": False,
                "TunnelOptions": [{
                    "OutsideIpAddress": "54.1.2.4",
                    "TunnelInsideCidr": "169.254.10.0/30",
                }]
            },
            "VgwTelemetry": [{
                "OutsideIpAddress": "54.1.2.4",
                "Status": "UP",
                "LastStatusChange": "2025-01-24T00:00:00Z",
                "AcceptedRouteCount": 5,
            }],
            "Tags": [{"Key": "Name", "Value": "Test VPN"}],
        }]
    }

    client.describe_customer_gateways.return_value = {
        "CustomerGateways": [{
            "CustomerGatewayId": "cgw-test123",
            "State": "available",
            "Type": "ipsec.1",
            "IpAddress": "203.0.113.1",
            "BgpAsn": "65000",
            "Tags": [{"Key": "Name", "Value": "Test CGW"}],
        }]
    }

    client.describe_vpn_gateways.return_value = {
        "VpnGateways": [{
            "VpnGatewayId": "vgw-test123",
            "State": "available",
            "Type": "ipsec.1",
            "VpcAttachments": [{
                "VpcId": "vpc-test123",
                "State": "attached",
            }],
            "AmazonSideAsn": 64512,
            "Tags": [{"Key": "Name", "Value": "Test VGW"}],
        }]
    }

    client.describe_dhcp_options.return_value = {
        "DhcpOptions": [{
            "DhcpOptionsId": "dopt-test123",
            "DhcpConfigurations": [
                {
                    "Key": "domain-name",
                    "Values": [{"Value": "ec2.internal"}]
                },
                {
                    "Key": "domain-name-servers",
                    "Values": [{"Value": "AmazonProvidedDNS"}]
                }
            ],
            "Tags": [{"Key": "Name", "Value": "Test DHCP"}],
        }]
    }

    client.describe_flow_logs.return_value = {
        "FlowLogs": [{
            "FlowLogId": "fl-test123",
            "ResourceId": "vpc-test123",
            "TrafficType": "ALL",
            "LogDestinationType": "cloud-watch-logs",
            "LogDestination": "arn:aws:logs:us-east-1:123456789012:log-group:/aws/vpc/flowlogs",
            "FlowLogStatus": "ACTIVE",
            "Tags": [{"Key": "Name", "Value": "Test Flow Log"}],
        }]
    }

    client.describe_network_interfaces.return_value = {
        "NetworkInterfaces": [{
            "NetworkInterfaceId": "eni-test123",
            "SubnetId": "subnet-test123",
            "VpcId": "vpc-test123",
            "Status": "in-use",
            "InterfaceType": "interface",
            "PrivateIpAddress": "10.0.1.10",
            "PrivateIpAddresses": [{
                "PrivateIpAddress": "10.0.1.10",
                "Primary": True,
            }],
            "Groups": [{
                "GroupId": "sg-test123",
                "GroupName": "test-sg",
            }],
            "Attachment": {
                "AttachmentId": "eni-attach-test123",
                "InstanceId": "i-test123",
                "Status": "attached",
            },
            "Tags": [{"Key": "Name", "Value": "Test ENI"}],
        }]
    }

    client.describe_virtual_interfaces.return_value = {
        "virtualInterfaces": [{
            "virtualInterfaceId": "dxvif-test123",
            "virtualInterfaceName": "Test VIF",
            "virtualInterfaceType": "private",
            "virtualInterfaceState": "available",
            "vlan": 100,
            "asn": 65000,
            "bgpPeers": [{
                "bgpPeerId": "peer-test123",
                "bgpStatus": "up",
                "bgpPeerState": "available",
                "asn": 65000,
                "addressFamily": "ipv4",
            }],
        }]
    }

    return client


def test_collect_all_sections(mock_aws_client: AWSClient) -> None:
    """Test that all 19 sections can be collected successfully."""
    vpc_id = "vpc-test123"

    # Collect all data
    result = collect_all_data_sync(mock_aws_client, vpc_id)

    # Verify basic structure
    assert result["vpc_id"] == vpc_id
    assert result["region"] == "us-east-1"
    assert result["profile"] == "test-profile"
    assert "sections" in result

    # Verify all 19 sections are present
    expected_sections = [
        "vpc",
        "vpc_attributes",
        "subnets",
        "route_tables",
        "security_groups",
        "network_acls",
        "internet_gateways",
        "nat_gateways",
        "elastic_ips",
        "vpc_endpoints",
        "vpc_peering",
        "transit_gateway_attachments",
        "vpn_connections",
        "customer_gateways",
        "vpn_gateways",
        "dhcp_options",
        "flow_logs",
        "network_interfaces",
        "direct_connect_vifs",
    ]

    sections = result["sections"]
    for section in expected_sections:
        assert section in sections, f"Section '{section}' not found in results"
        assert sections[section]["success"], f"Section '{section}' failed"
        assert "data" in sections[section], f"Section '{section}' has no data"


def test_console_output_rendering(mock_aws_client: AWSClient) -> None:
    """Test that console output can be rendered without errors."""
    vpc_id = "vpc-test123"

    # Collect data
    result = collect_all_data_sync(mock_aws_client, vpc_id)

    # Create a console instance
    console = Console()

    # Render console output (should not raise any exceptions)
    render_console_output(console, result)


def test_markdown_generation(mock_aws_client: AWSClient) -> None:
    """Test that markdown can be generated without errors."""
    vpc_id = "vpc-test123"

    # Collect data
    result = collect_all_data_sync(mock_aws_client, vpc_id)

    # Generate markdown
    markdown = generate_markdown(result)

    # Verify markdown structure
    assert "# VPC Network Details Report" in markdown
    assert "## Table of Contents" in markdown
    assert vpc_id in markdown

    # Verify all sections are in markdown
    assert "## VPC Overview" in markdown
    assert "## VPC Attributes" in markdown
    assert "## Subnets" in markdown
    assert "## Route Tables" in markdown
    assert "## Security Groups" in markdown
    assert "## Network ACLs" in markdown
    assert "## Internet Gateways" in markdown
    assert "## NAT Gateways" in markdown
    assert "## Elastic IPs" in markdown
    assert "## VPC Endpoints" in markdown
    assert "## VPC Peering Connections" in markdown
    assert "## Transit Gateway Attachments" in markdown
    assert "## VPN Connections" in markdown
    assert "## Customer Gateways" in markdown
    assert "## VPN Gateways" in markdown
    assert "## DHCP Options" in markdown
    assert "## VPC Flow Logs" in markdown
    assert "## Network Interfaces" in markdown
    assert "## Direct Connect Virtual Interfaces" in markdown


def test_section_filtering(mock_aws_client: AWSClient) -> None:
    """Test that section filtering works correctly."""
    vpc_id = "vpc-test123"

    # Collect only specific sections
    sections_to_collect = ["vpc", "subnets", "vpn_connections"]
    result = collect_all_data_sync(mock_aws_client, vpc_id, sections=sections_to_collect)

    # Verify only requested sections are present
    assert len(result["sections"]) == 3
    assert "vpc" in result["sections"]
    assert "subnets" in result["sections"]
    assert "vpn_connections" in result["sections"]

    # Verify other sections are not present
    assert "security_groups" not in result["sections"]
    assert "route_tables" not in result["sections"]


def test_vpn_tunnel_status_parsing(mock_aws_client: AWSClient) -> None:
    """Test that VPN tunnel status is correctly parsed."""
    vpc_id = "vpc-test123"

    result = collect_all_data_sync(mock_aws_client, vpc_id, sections=["vpn_connections"])

    vpn_data = result["sections"]["vpn_connections"]["data"]
    vpns = vpn_data["vpn_connections"]

    assert len(vpns) == 1
    vpn = vpns[0]

    # Verify tunnel status parsing
    assert vpn["tunnels_up"] == 1
    assert vpn["tunnels_down"] == 0
    assert vpn["all_tunnels_up"] is True
    assert len(vpn["vgw_telemetry"]) == 1


def test_network_interface_type_classification(mock_aws_client: AWSClient) -> None:
    """Test that network interface types are correctly classified."""
    vpc_id = "vpc-test123"

    result = collect_all_data_sync(mock_aws_client, vpc_id, sections=["network_interfaces"])

    eni_data = result["sections"]["network_interfaces"]["data"]
    enis = eni_data["network_interfaces"]

    assert len(enis) == 1
    eni = enis[0]

    # Verify interface type
    assert eni["interface_type"] == "interface"
    assert eni["status"] == "in-use"
    assert "attached_to" in eni


def test_direct_connect_bgp_status(mock_aws_client: AWSClient) -> None:
    """Test that Direct Connect BGP status is correctly parsed."""
    vpc_id = "vpc-test123"

    result = collect_all_data_sync(mock_aws_client, vpc_id, sections=["direct_connect_vifs"])

    vif_data = result["sections"]["direct_connect_vifs"]["data"]
    vifs = vif_data["virtual_interfaces"]

    assert len(vifs) == 1
    vif = vifs[0]

    # Verify BGP status parsing
    assert vif["bgp_sessions_up"] == 1
    assert vif["bgp_sessions_down"] == 0
    assert vif["all_bgp_sessions_up"] is True
    assert len(vif["bgp_peers"]) == 1


def test_vpc_attributes_parsing(mock_aws_client: AWSClient) -> None:
    """Test that VPC attributes are correctly parsed."""
    vpc_id = "vpc-test123"

    result = collect_all_data_sync(mock_aws_client, vpc_id, sections=["vpc_attributes"])

    attr_data = result["sections"]["vpc_attributes"]["data"]
    attrs = attr_data["attributes"]

    # Verify attributes
    assert attrs["enable_dns_support"] is True
    assert attrs["enable_dns_hostnames"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
