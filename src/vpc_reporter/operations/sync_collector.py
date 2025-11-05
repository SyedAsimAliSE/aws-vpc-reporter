"""Synchronous data collector for VPC resources."""

from __future__ import annotations

from typing import Any

from loguru import logger
from rich.progress import Progress

from vpc_reporter.aws.client import AWSClient
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


def collect_all_data_sync(
    aws_client: AWSClient,
    vpc_id: str,
    sections: list[str] | None = None,
    progress: Progress | None = None,
) -> dict[str, Any]:
    """Collect all VPC data synchronously.

    Args:
        aws_client: AWS client instance
        vpc_id: VPC ID to document
        sections: Optional list of sections to collect (default: all)
        progress: Optional Rich progress instance

    Returns:
        Dictionary containing all collected data
    """
    logger.info(f"Starting synchronous data collection for VPC {vpc_id}")

    # Initialize operations
    vpc_ops = VPCOperations(aws_client)
    subnet_ops = SubnetOperations(aws_client)
    route_table_ops = RouteTableOperations(aws_client)
    security_group_ops = SecurityGroupOperations(aws_client)
    network_acl_ops = NetworkACLOperations(aws_client)
    igw_ops = InternetGatewayOperations(aws_client)
    nat_ops = NATGatewayOperations(aws_client)
    eip_ops = ElasticIPOperations(aws_client)
    vpc_endpoint_ops = VPCEndpointOperations(aws_client)
    peering_ops = VPCPeeringOperations(aws_client)
    tgw_ops = TransitGatewayAttachmentOperations(aws_client)
    cgw_ops = CustomerGatewayOperations(aws_client)
    vgw_ops = VirtualPrivateGatewayOperations(aws_client)
    dhcp_ops = DHCPOptionsOperations(aws_client)
    flow_logs_ops = FlowLogsOperations(aws_client)
    vpn_ops = VPNConnectionOperations(aws_client)
    eni_ops = NetworkInterfaceOperations(aws_client)
    vpc_attr_ops = VPCAttributesOperations(aws_client)
    dx_vif_ops = DirectConnectVIFOperations(aws_client)

    # Get VPC details first to extract DHCP Options ID
    vpc_details = vpc_ops.get_vpc_details(vpc_id)
    dhcp_options_id = vpc_details.get("dhcp_options_id")

    # Define all sections
    all_sections = {
        "vpc": lambda: _collect_vpc(vpc_ops, vpc_id, progress),
        "vpc_attributes": lambda: _collect_vpc_attributes(
            vpc_attr_ops, vpc_id, progress
        ),
        "subnets": lambda: _collect_subnets(subnet_ops, vpc_id, progress),
        "route_tables": lambda: _collect_route_tables(
            route_table_ops, vpc_id, progress
        ),
        "internet_gateways": lambda: _collect_internet_gateways(
            igw_ops, vpc_id, progress
        ),
        "nat_gateways": lambda: _collect_nat_gateways(nat_ops, vpc_id, progress),
        "elastic_ips": lambda: _collect_elastic_ips(eip_ops, vpc_id, progress),
        "security_groups": lambda: _collect_security_groups(
            security_group_ops, vpc_id, progress
        ),
        "network_acls": lambda: _collect_network_acls(
            network_acl_ops, vpc_id, progress
        ),
        "vpc_endpoints": lambda: _collect_vpc_endpoints(
            vpc_endpoint_ops, vpc_id, progress
        ),
        "vpc_peering": lambda: _collect_vpc_peering(peering_ops, vpc_id, progress),
        "transit_gateway_attachments": lambda: _collect_transit_gateway_attachments(
            tgw_ops, vpc_id, progress
        ),
        "vpn_connections": lambda: _collect_vpn_connections(vpn_ops, progress),
        "customer_gateways": lambda: _collect_customer_gateways(cgw_ops, progress),
        "vpn_gateways": lambda: _collect_vpn_gateways(vgw_ops, vpc_id, progress),
        "dhcp_options": lambda: _collect_dhcp_options(
            dhcp_ops, dhcp_options_id, progress
        ),
        "flow_logs": lambda: _collect_flow_logs(flow_logs_ops, vpc_id, progress),
        "network_interfaces": lambda: _collect_network_interfaces(
            eni_ops, vpc_id, progress
        ),
        "direct_connect_vifs": lambda: _collect_direct_connect_vifs(
            dx_vif_ops, progress
        ),
    }

    # Determine which sections to collect
    if sections:
        sections_to_collect = {k: v for k, v in all_sections.items() if k in sections}
    else:
        sections_to_collect = all_sections

    # Collect data
    data: dict[str, Any] = {
        "vpc_id": vpc_id,
        "region": aws_client.region,
        "profile": aws_client.profile,
        "sections": {},
    }

    for section_name, collector_func in sections_to_collect.items():
        try:
            data["sections"][section_name] = collector_func()
        except Exception as e:
            logger.error(f"Error collecting {section_name}: {e}")
            data["sections"][section_name] = {
                "error": str(e),
                "success": False,
            }

    logger.info("Data collection complete")
    return data


def _collect_vpc(
    vpc_ops: VPCOperations,
    vpc_id: str,
    progress: Progress | None,
) -> dict[str, Any]:
    """Collect VPC data."""
    if progress:
        task = progress.add_task("[cyan]Collecting VPC overview...", total=None)

    try:
        data = vpc_ops.get_vpc_details(vpc_id)
        if progress:
            progress.update(task, description="[green]✓ VPC overview")
        return {"success": True, "data": data}
    finally:
        if progress:
            progress.remove_task(task)


def _collect_subnets(
    subnet_ops: SubnetOperations,
    vpc_id: str,
    progress: Progress | None,
) -> dict[str, Any]:
    """Collect subnet data."""
    if progress:
        task = progress.add_task("[cyan]Collecting subnets...", total=None)

    try:
        data = subnet_ops.get_subnets(vpc_id)
        if progress:
            progress.update(
                task, description=f"[green]✓ Subnets ({data['total_count']})"
            )
        return {"success": True, "data": data}
    finally:
        if progress:
            progress.remove_task(task)


def _collect_route_tables(
    route_table_ops: RouteTableOperations,
    vpc_id: str,
    progress: Progress | None,
) -> dict[str, Any]:
    """Collect route table data."""
    if progress:
        task = progress.add_task("[cyan]Collecting route tables...", total=None)

    try:
        data = route_table_ops.get_route_tables(vpc_id)
        if progress:
            progress.update(
                task, description=f"[green]✓ Route tables ({data['total_count']})"
            )
        return {"success": True, "data": data}
    finally:
        if progress:
            progress.remove_task(task)


def _collect_security_groups(
    security_group_ops: SecurityGroupOperations,
    vpc_id: str,
    progress: Progress | None,
) -> dict[str, Any]:
    """Collect security group data."""
    if progress:
        task = progress.add_task("[cyan]Collecting security groups...", total=None)

    try:
        data = security_group_ops.get_security_groups(vpc_id)
        if progress:
            progress.update(
                task, description=f"[green]✓ Security groups ({data['total_count']})"
            )
        return {"success": True, "data": data}
    finally:
        if progress:
            progress.remove_task(task)


def _collect_network_acls(
    network_acl_ops: NetworkACLOperations,
    vpc_id: str,
    progress: Progress | None,
) -> dict[str, Any]:
    """Collect network ACL data."""
    if progress:
        task = progress.add_task("[cyan]Collecting network ACLs...", total=None)

    try:
        data = network_acl_ops.get_network_acls(vpc_id)
        if progress:
            progress.update(
                task, description=f"[green]✓ Network ACLs ({data['total_count']})"
            )
        return {"success": True, "data": data}
    finally:
        if progress:
            progress.remove_task(task)


def _collect_internet_gateways(
    igw_ops: InternetGatewayOperations,
    vpc_id: str,
    progress: Progress | None,
) -> dict[str, Any]:
    """Collect internet gateway data."""
    if progress:
        task = progress.add_task("[cyan]Collecting internet gateways...", total=None)

    try:
        data = igw_ops.get_internet_gateways(vpc_id)
        if progress:
            progress.update(
                task, description=f"[green]✓ Internet gateways ({data['total_count']})"
            )
        return {"success": True, "data": data}
    finally:
        if progress:
            progress.remove_task(task)


def _collect_nat_gateways(
    nat_ops: NATGatewayOperations,
    vpc_id: str,
    progress: Progress | None,
) -> dict[str, Any]:
    """Collect NAT gateway data."""
    if progress:
        task = progress.add_task("[cyan]Collecting NAT gateways...", total=None)

    try:
        data = nat_ops.get_nat_gateways(vpc_id)
        if progress:
            progress.update(
                task, description=f"[green]✓ NAT gateways ({data['total_count']})"
            )
        return {"success": True, "data": data}
    finally:
        if progress:
            progress.remove_task(task)


def _collect_elastic_ips(
    eip_ops: ElasticIPOperations,
    vpc_id: str,
    progress: Progress | None,
) -> dict[str, Any]:
    """Collect Elastic IP data."""
    if progress:
        task = progress.add_task("[cyan]Collecting Elastic IPs...", total=None)

    try:
        data = eip_ops.get_elastic_ips(vpc_id)
        if progress:
            progress.update(
                task, description=f"[green]✓ Elastic IPs ({data['total_count']})"
            )
        return {"success": True, "data": data}
    finally:
        if progress:
            progress.remove_task(task)


def _collect_vpc_endpoints(
    vpc_endpoint_ops: VPCEndpointOperations,
    vpc_id: str,
    progress: Progress | None,
) -> dict[str, Any]:
    """Collect VPC endpoint data."""
    if progress:
        task = progress.add_task("[cyan]Collecting VPC endpoints...", total=None)

    try:
        data = vpc_endpoint_ops.get_vpc_endpoints(vpc_id)
        if progress:
            progress.update(
                task, description=f"[green]✓ VPC endpoints ({data['total_count']})"
            )
        return {"success": True, "data": data}
    finally:
        if progress:
            progress.remove_task(task)


def _collect_vpc_peering(
    peering_ops: VPCPeeringOperations,
    vpc_id: str,
    progress: Progress | None,
) -> dict[str, Any]:
    """Collect VPC peering connection data."""
    if progress:
        task = progress.add_task(
            "[cyan]Collecting VPC peering connections...", total=None
        )

    try:
        data = peering_ops.get_vpc_peering_connections(vpc_id)
        if progress:
            progress.update(
                task, description=f"[green]✓ VPC peering ({data['total_count']})"
            )
        return {"success": True, "data": data}
    finally:
        if progress:
            progress.remove_task(task)


def _collect_transit_gateway_attachments(
    tgw_ops: TransitGatewayAttachmentOperations,
    vpc_id: str,
    progress: Progress | None,
) -> dict[str, Any]:
    """Collect Transit Gateway attachment data."""
    if progress:
        task = progress.add_task(
            "[cyan]Collecting Transit Gateway attachments...", total=None
        )

    try:
        data = tgw_ops.get_transit_gateway_attachments(vpc_id)
        if progress:
            progress.update(
                task,
                description=f"[green]✓ Transit Gateway attachments ({data['total_count']})",
            )
        return {"success": True, "data": data}
    finally:
        if progress:
            progress.remove_task(task)


def _collect_vpn_connections(
    vpn_ops: VPNConnectionOperations,
    progress: Progress | None,
) -> dict[str, Any]:
    """Collect VPN connection data."""
    if progress:
        task = progress.add_task("[cyan]Collecting VPN connections...", total=None)

    try:
        data = vpn_ops.get_vpn_connections()
        if progress:
            progress.update(
                task, description=f"[green]✓ VPN connections ({data['total_count']})"
            )
        return {"success": True, "data": data}
    finally:
        if progress:
            progress.remove_task(task)


def _collect_customer_gateways(
    cgw_ops: CustomerGatewayOperations,
    progress: Progress | None,
) -> dict[str, Any]:
    """Collect Customer Gateway data."""
    if progress:
        task = progress.add_task("[cyan]Collecting Customer Gateways...", total=None)

    try:
        data = cgw_ops.get_customer_gateways()
        if progress:
            progress.update(
                task, description=f"[green]✓ Customer Gateways ({data['total_count']})"
            )
        return {"success": True, "data": data}
    finally:
        if progress:
            progress.remove_task(task)


def _collect_vpn_gateways(
    vgw_ops: VirtualPrivateGatewayOperations,
    vpc_id: str,
    progress: Progress | None,
) -> dict[str, Any]:
    """Collect VPN Gateway data."""
    if progress:
        task = progress.add_task("[cyan]Collecting VPN Gateways...", total=None)

    try:
        data = vgw_ops.get_vpn_gateways(vpc_id)
        if progress:
            progress.update(
                task, description=f"[green]✓ VPN Gateways ({data['total_count']})"
            )
        return {"success": True, "data": data}
    finally:
        if progress:
            progress.remove_task(task)


def _collect_dhcp_options(
    dhcp_ops: DHCPOptionsOperations,
    dhcp_options_id: str | None,
    progress: Progress | None,
) -> dict[str, Any]:
    """Collect DHCP Options data.

    Args:
        dhcp_ops: DHCP options operations instance
        dhcp_options_id: DHCP Options Set ID from VPC (can be None)
        progress: Progress tracker
    """
    if progress:
        task = progress.add_task("[cyan]Collecting DHCP Options...", total=None)

    try:
        data = dhcp_ops.get_dhcp_options(dhcp_options_id or "")
        dhcp_id = data.get("dhcp_options_id", "None")
        if progress:
            progress.update(task, description=f"[green]✓ DHCP Options ({dhcp_id})")
        return {"success": True, "data": data}
    finally:
        if progress:
            progress.remove_task(task)


def _collect_flow_logs(
    flow_logs_ops: FlowLogsOperations,
    vpc_id: str,
    progress: Progress | None,
) -> dict[str, Any]:
    """Collect VPC Flow Logs data."""
    if progress:
        task = progress.add_task("[cyan]Collecting VPC Flow Logs...", total=None)

    try:
        data = flow_logs_ops.get_flow_logs(vpc_id)
        if progress:
            progress.update(
                task, description=f"[green]✓ VPC Flow Logs ({data['total_count']})"
            )
        return {"success": True, "data": data}
    finally:
        if progress:
            progress.remove_task(task)


def _collect_network_interfaces(
    eni_ops: NetworkInterfaceOperations,
    vpc_id: str,
    progress: Progress | None,
) -> dict[str, Any]:
    """Collect Network Interface data."""
    if progress:
        task = progress.add_task("[cyan]Collecting Network Interfaces...", total=None)

    try:
        data = eni_ops.get_network_interfaces(vpc_id)
        if progress:
            progress.update(
                task, description=f"[green]✓ Network Interfaces ({data['total_count']})"
            )
        return {"success": True, "data": data}
    finally:
        if progress:
            progress.remove_task(task)


def _collect_vpc_attributes(
    vpc_attr_ops: VPCAttributesOperations,
    vpc_id: str,
    progress: Progress | None,
) -> dict[str, Any]:
    """Collect VPC Attributes data."""
    if progress:
        task = progress.add_task("[cyan]Collecting VPC Attributes...", total=None)

    try:
        data = vpc_attr_ops.get_vpc_attributes(vpc_id)
        if progress:
            progress.update(task, description="[green]✓ VPC Attributes")
        return {"success": True, "data": data}
    finally:
        if progress:
            progress.remove_task(task)


def _collect_direct_connect_vifs(
    dx_vif_ops: DirectConnectVIFOperations,
    progress: Progress | None,
) -> dict[str, Any]:
    """Collect Direct Connect Virtual Interface data."""
    if progress:
        task = progress.add_task("[cyan]Collecting Direct Connect VIFs...", total=None)

    try:
        data = dx_vif_ops.get_virtual_interfaces()
        if progress:
            progress.update(
                task,
                description=f"[green]✓ Direct Connect VIFs ({data['total_count']})",
            )
        return {"success": True, "data": data}
    finally:
        if progress:
            progress.remove_task(task)
