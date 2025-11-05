"""Operations module for VPC data collection."""

from __future__ import annotations


__all__ = [
    "VPCOperations",
    "SubnetOperations",
    "RouteTableOperations",
    "SecurityGroupOperations",
    "NetworkACLOperations",
    "InternetGatewayOperations",
    "NATGatewayOperations",
    "ElasticIPOperations",
    "VPCEndpointOperations",
    "VPCPeeringOperations",
    "TransitGatewayAttachmentOperations",
    "CustomerGatewayOperations",
    "VirtualPrivateGatewayOperations",
    "DHCPOptionsOperations",
    "FlowLogsOperations",
    "VPNConnectionOperations",
    "NetworkInterfaceOperations",
    "VPCAttributesOperations",
    "DirectConnectVIFOperations",
]

from vpc_reporter.operations.cgw_ops import CustomerGatewayOperations
from vpc_reporter.operations.dhcp_ops import DHCPOptionsOperations
from vpc_reporter.operations.dx_vif_ops import DirectConnectVIFOperations
from vpc_reporter.operations.eip_ops import ElasticIPOperations
from vpc_reporter.operations.eni_ops import NetworkInterfaceOperations
from vpc_reporter.operations.flow_logs_ops import FlowLogsOperations
from vpc_reporter.operations.igw_ops import InternetGatewayOperations
from vpc_reporter.operations.nat_ops import NATGatewayOperations
from vpc_reporter.operations.network_acl_ops import NetworkACLOperations
from vpc_reporter.operations.peering_ops import VPCPeeringOperations
from vpc_reporter.operations.route_table_ops import RouteTableOperations
from vpc_reporter.operations.security_group_ops import SecurityGroupOperations
from vpc_reporter.operations.subnet_ops import SubnetOperations
from vpc_reporter.operations.tgw_ops import TransitGatewayAttachmentOperations
from vpc_reporter.operations.vgw_ops import VirtualPrivateGatewayOperations
from vpc_reporter.operations.vpc_attributes_ops import VPCAttributesOperations
from vpc_reporter.operations.vpc_endpoint_ops import VPCEndpointOperations
from vpc_reporter.operations.vpc_ops import VPCOperations
from vpc_reporter.operations.vpn_ops import VPNConnectionOperations
