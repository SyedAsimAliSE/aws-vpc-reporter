"""Asynchronous data collector for VPC resources."""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from loguru import logger

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


async def collect_all_data_async(
    aws_client: AWSClient,
    vpc_id: str,
    sections: list[str] | None = None,
) -> dict[str, Any]:
    """Collect all VPC data asynchronously using concurrent execution.

    This implementation uses ThreadPoolExecutor to run boto3 calls concurrently,
    providing significant performance improvements for large VPCs.

    Args:
        aws_client: AWS client instance
        vpc_id: VPC ID to document
        sections: Optional list of sections to collect (default: all)

    Returns:
        Dictionary containing all collected data
    """
    logger.info(f"Starting asynchronous data collection for VPC {vpc_id}")

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
    vpc_details = await _run_in_executor(vpc_ops.get_vpc_details, vpc_id)
    dhcp_options_id = vpc_details.get("dhcp_options_id")

    # Define all section collectors
    all_collectors = {
        "vpc": lambda: vpc_ops.get_vpc_details(vpc_id),
        "vpc_attributes": lambda: vpc_attr_ops.get_vpc_attributes(vpc_id),
        "subnets": lambda: subnet_ops.get_subnets(vpc_id),
        "route_tables": lambda: route_table_ops.get_route_tables(vpc_id),
        "security_groups": lambda: security_group_ops.get_security_groups(vpc_id),
        "network_acls": lambda: network_acl_ops.get_network_acls(vpc_id),
        "internet_gateways": lambda: igw_ops.get_internet_gateways(vpc_id),
        "nat_gateways": lambda: nat_ops.get_nat_gateways(vpc_id),
        "elastic_ips": lambda: eip_ops.get_elastic_ips(vpc_id),
        "vpc_endpoints": lambda: vpc_endpoint_ops.get_vpc_endpoints(vpc_id),
        "vpc_peering": lambda: peering_ops.get_vpc_peering_connections(vpc_id),
        "transit_gateway_attachments": lambda: tgw_ops.get_transit_gateway_attachments(
            vpc_id
        ),
        "vpn_connections": lambda: vpn_ops.get_vpn_connections(),
        "customer_gateways": lambda: cgw_ops.get_customer_gateways(),
        "vpn_gateways": lambda: vgw_ops.get_vpn_gateways(vpc_id),
        "dhcp_options": lambda: dhcp_ops.get_dhcp_options(dhcp_options_id or ""),
        "flow_logs": lambda: flow_logs_ops.get_flow_logs(vpc_id),
        "network_interfaces": lambda: eni_ops.get_network_interfaces(vpc_id),
        "direct_connect_vifs": lambda: dx_vif_ops.get_virtual_interfaces(),
    }

    # Determine which sections to collect
    if sections:
        collectors_to_run = {k: v for k, v in all_collectors.items() if k in sections}
    else:
        collectors_to_run = all_collectors

    # Collect data concurrently
    logger.info(f"Collecting {len(collectors_to_run)} sections concurrently")

    tasks = {
        section_name: _collect_section_async(section_name, collector_func)
        for section_name, collector_func in collectors_to_run.items()
    }

    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks.values(), return_exceptions=True)

    # Build result dictionary
    data: dict[str, Any] = {
        "vpc_id": vpc_id,
        "region": aws_client.region,
        "profile": aws_client.profile,
        "sections": {},
    }

    # Process results
    for section_name, result in zip(tasks.keys(), results, strict=False):
        if isinstance(result, Exception):
            logger.error(f"Error collecting {section_name}: {result}")
            data["sections"][section_name] = {
                "error": str(result),
                "success": False,
            }
        else:
            data["sections"][section_name] = result

    logger.info("Async data collection complete")
    return data


async def _collect_section_async(
    section_name: str,
    collector_func: Any,
) -> dict[str, Any]:
    """Collect a single section asynchronously.

    Args:
        section_name: Name of the section
        collector_func: Function to call for collection

    Returns:
        Section data dictionary
    """
    try:
        logger.debug(f"Collecting {section_name}")
        data = await _run_in_executor(collector_func)
        logger.debug(f"Completed {section_name}")
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Error collecting {section_name}: {e}")
        return {"success": False, "error": str(e)}


async def _run_in_executor(func: Any, *args: Any) -> Any:
    """Run a synchronous function in a thread pool executor.

    Args:
        func: Function to run
        *args: Arguments to pass to the function

    Returns:
        Function result
    """
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=10) as executor:
        return await loop.run_in_executor(executor, func, *args)
