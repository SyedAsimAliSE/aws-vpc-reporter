"""Markdown report generator."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any


def generate_markdown(data: dict[str, Any]) -> str:
    """Generate markdown report from collected data.

    Args:
        data: Collected VPC data

    Returns:
        Markdown formatted string
    """
    vpc_id = data.get("vpc_id", "Unknown")
    region = data.get("region", "Unknown")
    profile = data.get("profile", "Unknown")
    sections = data.get("sections", {})

    # Build markdown
    md_parts = []

    # Header
    md_parts.append(_generate_header(vpc_id, region, profile, sections))

    # Table of Contents
    md_parts.append(_generate_toc(sections))

    # VPC Overview
    if "vpc" in sections:
        md_parts.append(_generate_vpc_section(sections["vpc"]))

    # Subnets
    if "subnets" in sections:
        md_parts.append(_generate_subnets_section(sections["subnets"]))

    # Route Tables
    if "route_tables" in sections:
        md_parts.append(_generate_route_tables_section(sections["route_tables"]))

    # Security Groups
    if "security_groups" in sections:
        md_parts.append(_generate_security_groups_section(sections["security_groups"]))

    # Network ACLs
    if "network_acls" in sections:
        md_parts.append(_generate_network_acls_section(sections["network_acls"]))

    # Internet Gateways
    if "internet_gateways" in sections:
        md_parts.append(_generate_internet_gateways_section(sections["internet_gateways"]))

    # NAT Gateways
    if "nat_gateways" in sections:
        md_parts.append(_generate_nat_gateways_section(sections["nat_gateways"]))

    # Elastic IPs
    if "elastic_ips" in sections:
        md_parts.append(_generate_elastic_ips_section(sections["elastic_ips"]))

    # VPC Endpoints
    if "vpc_endpoints" in sections:
        md_parts.append(_generate_vpc_endpoints_section(sections["vpc_endpoints"]))

    # VPC Peering
    if "vpc_peering" in sections:
        md_parts.append(_generate_vpc_peering_section(sections["vpc_peering"]))

    # Transit Gateway Attachments
    if "transit_gateway_attachments" in sections:
        md_parts.append(_generate_transit_gateway_section(sections["transit_gateway_attachments"]))

    # VPN Connections
    if "vpn_connections" in sections:
        md_parts.append(_generate_vpn_connections_section(sections["vpn_connections"]))

    # Customer Gateways
    if "customer_gateways" in sections:
        md_parts.append(_generate_customer_gateways_section(sections["customer_gateways"]))

    # VPN Gateways
    if "vpn_gateways" in sections:
        md_parts.append(_generate_vpn_gateways_section(sections["vpn_gateways"]))

    # DHCP Options
    if "dhcp_options" in sections:
        md_parts.append(_generate_dhcp_options_section(sections["dhcp_options"]))

    # Flow Logs
    if "flow_logs" in sections:
        md_parts.append(_generate_flow_logs_section(sections["flow_logs"]))

    # Network Interfaces
    if "network_interfaces" in sections:
        md_parts.append(_generate_network_interfaces_section(sections["network_interfaces"]))

    # VPC Attributes
    if "vpc_attributes" in sections:
        md_parts.append(_generate_vpc_attributes_section(sections["vpc_attributes"]))

    # Direct Connect VIFs
    if "direct_connect_vifs" in sections:
        md_parts.append(_generate_direct_connect_vifs_section(sections["direct_connect_vifs"]))

    # Footer
    md_parts.append(_generate_footer())

    return "\n\n".join(md_parts)


def _generate_header(vpc_id: str, region: str, profile: str, sections: dict[str, Any]) -> str:
    """Generate report header."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")

    return f"""# VPC Network Details Report

**Generated:** {timestamp}
**AWS Profile:** {profile}
**Region:** {region}
**VPC ID:** {vpc_id}
**Sections:** {len(sections)}

---"""


def _generate_toc(sections: dict[str, Any]) -> str:
    """Generate table of contents."""
    toc_items = []

    section_titles = {
        "vpc": "VPC Overview",
        "vpc_attributes": "VPC Attributes",
        "subnets": "Subnets",
        "route_tables": "Route Tables",
        "security_groups": "Security Groups",
        "network_acls": "Network ACLs",
        "internet_gateways": "Internet Gateways",
        "nat_gateways": "NAT Gateways",
        "elastic_ips": "Elastic IPs",
        "vpc_endpoints": "VPC Endpoints",
        "vpc_peering": "VPC Peering Connections",
        "transit_gateway_attachments": "Transit Gateway Attachments",
        "vpn_connections": "VPN Connections",
        "customer_gateways": "Customer Gateways",
        "vpn_gateways": "VPN Gateways",
        "dhcp_options": "DHCP Options",
        "flow_logs": "VPC Flow Logs",
        "network_interfaces": "Network Interfaces",
        "direct_connect_vifs": "Direct Connect Virtual Interfaces",
    }

    for idx, (key, title) in enumerate(section_titles.items(), 1):
        if key in sections:
            anchor = title.lower().replace(" ", "-")
            toc_items.append(f"{idx}. [{title}](#{anchor})")

    return "## Table of Contents\n\n" + "\n".join(toc_items) + "\n\n---"


def _generate_vpc_section(section_data: dict[str, Any]) -> str:
    """Generate VPC overview section."""
    if not section_data.get("success"):
        return "## VPC Overview\n\n**Error:** Unable to retrieve VPC details"

    vpc = section_data["data"]

    md = "## VPC Overview\n\n"
    md += f"**VPC ID:** {vpc['vpc_id']}  \n"
    md += f"**Name:** {vpc.get('name', '<No Name>')}  \n"
    md += f"**CIDR Block:** {vpc['cidr_block']}  \n"
    md += f"**State:** {vpc['state']}  \n"
    md += f"**Instance Tenancy:** {vpc.get('instance_tenancy', 'default')}  \n"
    md += f"**Default VPC:** {'Yes' if vpc.get('is_default') else 'No'}  \n"
    md += f"**DHCP Options ID:** {vpc.get('dhcp_options_id', 'N/A')}  \n"

    # IPv6 CIDR blocks
    if vpc.get("ipv6_cidr_blocks"):
        md += "\n**IPv6 CIDR Blocks:**\n"
        for cidr in vpc["ipv6_cidr_blocks"]:
            md += f"- {cidr}\n"

    # Raw JSON
    md += "\n### Full VPC Details\n\n"
    md += "```json\n"
    md += json.dumps(vpc.get("raw_data", {}), indent=2, default=str)
    md += "\n```"

    return md


def _generate_subnets_section(section_data: dict[str, Any]) -> str:
    """Generate subnets section."""
    if not section_data.get("success"):
        return "## Subnets\n\n**Error:** Unable to retrieve subnets"

    data = section_data["data"]
    subnets = data.get("subnets", [])

    md = f"## Subnets\n\n**Total Subnets:** {data['total_count']}\n\n"

    # Summary table
    md += "### Subnet Summary\n\n"
    md += "| Subnet ID | Name | CIDR | AZ | Available IPs | Public | State |\n"
    md += "|-----------|------|------|----|--------------:|--------|-------|\n"

    for subnet in subnets:
        md += f"| {subnet['subnet_id']} | "
        md += f"{subnet.get('name', '<No Name>')} | "
        md += f"{subnet['cidr_block']} | "
        md += f"{subnet['availability_zone']} | "
        md += f"{subnet['available_ip_count']} | "
        md += f"{'Yes' if subnet['map_public_ip'] else 'No'} | "
        md += f"{subnet['state']} |\n"

    # Raw JSON
    md += "\n### Full Subnet Details\n\n"
    md += "```json\n"
    md += json.dumps(data.get("raw_data", []), indent=2, default=str)
    md += "\n```"

    return md


def _generate_route_tables_section(section_data: dict[str, Any]) -> str:
    """Generate route tables section."""
    if not section_data.get("success"):
        return "## Route Tables\n\n**Error:** Unable to retrieve route tables"

    data = section_data["data"]
    route_tables = data.get("route_tables", [])

    md = f"## Route Tables\n\n**Total Route Tables:** {data['total_count']}\n\n"

    # Detailed view for each route table
    for rt in route_tables:
        rt_type = "Main" if rt["is_main"] else "Custom"
        md += f"### {rt['route_table_id']} - {rt.get('name', '<No Name>')} ({rt_type})\n\n"

        # Associated subnets
        md += "**Associated Subnets:**\n"
        if rt["associated_subnets"]:
            for subnet_id in rt["associated_subnets"]:
                md += f"- {subnet_id}\n"
        else:
            md += "- None (Main route table)\n"

        # Routes
        md += "\n**Routes:**\n\n"
        md += "| Destination | Target | Status | Origin |\n"
        md += "|-------------|--------|--------|--------|\n"

        for route in rt["routes"]:
            md += f"| {route['destination']} | "
            md += f"{route['target']} | "
            md += f"{route['state']} | "
            md += f"{route['origin']} |\n"

        md += "\n"

    # Raw JSON
    md += "### Full Route Table Details\n\n"
    md += "```json\n"
    md += json.dumps(data.get("raw_data", []), indent=2, default=str)
    md += "\n```"

    return md


def _generate_security_groups_section(section_data: dict[str, Any]) -> str:
    """Generate security groups section."""
    if not section_data.get("success"):
        return "## Security Groups\n\n**Error:** Unable to retrieve security groups"

    data = section_data["data"]
    security_groups = data.get("security_groups", [])

    md = f"## Security Groups\n\n**Total Security Groups:** {data['total_count']}\n\n"

    # Summary table
    md += "### Security Group Summary\n\n"
    md += "| Group ID | Name | Description | Inbound Rules | Outbound Rules |\n"
    md += "|----------|------|-------------|---------------:|----------------:|\n"

    for sg in security_groups:
        md += f"| {sg['group_id']} | "
        md += f"{sg.get('name', sg['group_name'])} | "
        md += f"{sg['description'][:50]}{'...' if len(sg['description']) > 50 else ''} | "
        md += f"{sg['inbound_rules_count']} | "
        md += f"{sg['outbound_rules_count']} |\n"

    # Detailed rules for each security group
    md += "\n### Detailed Security Group Rules\n\n"

    for sg in security_groups:
        md += f"#### {sg['group_id']} - {sg.get('name', sg['group_name'])}\n\n"
        md += f"**Description:** {sg['description']}  \n"
        md += f"**VPC ID:** {sg.get('vpc_id', 'N/A')}  \n"
        md += f"**Owner ID:** {sg.get('owner_id', 'N/A')}  \n\n"

        # Inbound rules
        if sg["inbound_rules"]:
            md += "**Inbound Rules:**\n\n"
            md += "| Type | Protocol | Port | Source | Description |\n"
            md += "|------|----------|------|--------|-------------|\n"

            for rule in sg["inbound_rules"]:
                md += f"| {rule['type']} | "
                md += f"{rule['protocol']} | "
                md += f"{rule['port_range']} | "
                md += f"{rule['source']} | "
                md += f"{rule.get('description', '')} |\n"
            md += "\n"
        else:
            md += "**Inbound Rules:** None\n\n"

        # Outbound rules
        if sg["outbound_rules"]:
            md += "**Outbound Rules:**\n\n"
            md += "| Type | Protocol | Port | Destination | Description |\n"
            md += "|------|----------|------|-------------|-------------|\n"

            for rule in sg["outbound_rules"]:
                md += f"| {rule['type']} | "
                md += f"{rule['protocol']} | "
                md += f"{rule['port_range']} | "
                md += f"{rule['source']} | "
                md += f"{rule.get('description', '')} |\n"
            md += "\n"
        else:
            md += "**Outbound Rules:** None\n\n"

    # Raw JSON
    md += "### Full Security Group Details (JSON)\n\n"
    md += "```json\n"
    md += json.dumps(data.get("raw_data", []), indent=2, default=str)
    md += "\n```"

    return md


def _generate_network_acls_section(section_data: dict[str, Any]) -> str:
    """Generate network ACLs section."""
    if not section_data.get("success"):
        return "## Network ACLs\n\n**Error:** Unable to retrieve network ACLs"

    data = section_data["data"]
    network_acls = data.get("network_acls", [])

    md = f"## Network ACLs\n\n**Total Network ACLs:** {data['total_count']}\n\n"

    # Summary table
    md += "### Network ACL Summary\n\n"
    md += "| NACL ID | Name | Default | Subnets | Inbound Rules | Outbound Rules |\n"
    md += "|---------|------|---------|--------:|--------------:|---------------:|\n"

    for nacl in network_acls:
        md += f"| {nacl['network_acl_id']} | "
        md += f"{nacl.get('name', '<No Name>')} | "
        md += f"{'Yes' if nacl['is_default'] else 'No'} | "
        md += f"{nacl['associated_subnet_count']} | "
        md += f"{nacl['inbound_rules_count']} | "
        md += f"{nacl['outbound_rules_count']} |\n"

    # Detailed rules for each NACL
    md += "\n### Detailed Network ACL Rules\n\n"

    for nacl in network_acls:
        md += f"#### {nacl['network_acl_id']} - {nacl.get('name', '<No Name>')}\n\n"
        md += f"**Default:** {'Yes' if nacl['is_default'] else 'No'}  \n"
        md += f"**VPC ID:** {nacl.get('vpc_id', 'N/A')}  \n"
        md += f"**Owner ID:** {nacl.get('owner_id', 'N/A')}  \n"
        md += f"**Associated Subnets:** {nacl['associated_subnet_count']}  \n\n"

        # List associated subnets
        if nacl.get("associations"):
            md += "**Subnet Associations:**\n"
            for assoc in nacl["associations"]:
                if assoc.get("subnet_id"):
                    md += f"- {assoc['subnet_id']}\n"
            md += "\n"

        # Inbound rules
        if nacl["inbound_rules"]:
            md += "**Inbound Rules:**\n\n"
            md += "| Rule # | Action | Protocol | Port | Source | ICMP |\n"
            md += "|-------:|--------|----------|------|--------|------|\n"

            for rule in nacl["inbound_rules"]:
                md += f"| {rule['rule_number']} | "
                md += f"{rule['rule_action']} | "
                md += f"{rule['protocol']} | "
                md += f"{rule['port_range']} | "
                md += f"{rule['cidr_block']} | "
                md += f"{rule.get('icmp_info', '')} |\n"
            md += "\n"
        else:
            md += "**Inbound Rules:** None\n\n"

        # Outbound rules
        if nacl["outbound_rules"]:
            md += "**Outbound Rules:**\n\n"
            md += "| Rule # | Action | Protocol | Port | Destination | ICMP |\n"
            md += "|-------:|--------|----------|------|-------------|------|\n"

            for rule in nacl["outbound_rules"]:
                md += f"| {rule['rule_number']} | "
                md += f"{rule['rule_action']} | "
                md += f"{rule['protocol']} | "
                md += f"{rule['port_range']} | "
                md += f"{rule['cidr_block']} | "
                md += f"{rule.get('icmp_info', '')} |\n"
            md += "\n"
        else:
            md += "**Outbound Rules:** None\n\n"

    # Raw JSON
    md += "### Full Network ACL Details (JSON)\n\n"
    md += "```json\n"
    md += json.dumps(data.get("raw_data", []), indent=2, default=str)
    md += "\n```"

    return md


def _generate_internet_gateways_section(section_data: dict[str, Any]) -> str:
    """Generate Internet Gateways section."""
    if not section_data.get("success"):
        return "## Internet Gateways\n\n**Error:** Unable to retrieve internet gateways"

    data = section_data["data"]
    igws = data.get("internet_gateways", [])

    md = f"## Internet Gateways\n\n**Total Internet Gateways:** {data['total_count']}\n\n"

    if not igws:
        md += "*No internet gateways found*\n"
        return md

    md += "| IGW ID | Name | State | Owner ID |\n"
    md += "|--------|------|-------|----------|\n"

    for igw in igws:
        md += f"| {igw['internet_gateway_id']} | "
        md += f"{igw.get('name', '<No Name>')} | "
        md += f"{igw['attachment_state']} | "
        md += f"{igw['owner_id']} |\n"

    return md


def _generate_nat_gateways_section(section_data: dict[str, Any]) -> str:
    """Generate NAT Gateways section."""
    if not section_data.get("success"):
        return "## NAT Gateways\n\n**Error:** Unable to retrieve NAT gateways"

    data = section_data["data"]
    nat_gws = data.get("nat_gateways", [])

    md = f"## NAT Gateways\n\n**Total NAT Gateways:** {data['total_count']}\n\n"

    if not nat_gws:
        md += "*No NAT gateways found*\n"
        return md

    md += "| NAT GW ID | Name | State | Subnet ID | Public IP(s) |\n"
    md += "|-----------|------|-------|-----------|-------------|\n"

    for nat in nat_gws:
        public_ips = ", ".join([addr["public_ip"] for addr in nat["nat_gateway_addresses"] if addr.get("public_ip")])
        md += f"| {nat['nat_gateway_id']} | "
        md += f"{nat.get('name', '<No Name>')} | "
        md += f"{nat['state']} | "
        md += f"{nat['subnet_id']} | "
        md += f"{public_ips} |\n"

    return md


def _generate_elastic_ips_section(section_data: dict[str, Any]) -> str:
    """Generate Elastic IPs section."""
    if not section_data.get("success"):
        return "## Elastic IPs\n\n**Error:** Unable to retrieve Elastic IPs"

    data = section_data["data"]
    eips = data.get("elastic_ips", [])

    md = f"## Elastic IPs\n\n**Total Elastic IPs:** {data['total_count']}\n\n"

    if not eips:
        md += "*No Elastic IPs found*\n"
        return md

    md += "| Public IP | Name | Allocation ID | Associated | Instance/ENI |\n"
    md += "|-----------|------|---------------|------------|-------------|\n"

    for eip in eips:
        associated = "Yes" if eip["is_associated"] else "No"
        resource = eip.get("instance_id") or eip.get("network_interface_id") or "-"
        md += f"| {eip['public_ip']} | "
        md += f"{eip.get('name', '<No Name>')} | "
        md += f"{eip.get('allocation_id', '-')} | "
        md += f"{associated} | "
        md += f"{resource} |\n"

    return md


def _generate_vpc_endpoints_section(section_data: dict[str, Any]) -> str:
    """Generate VPC Endpoints section."""
    if not section_data.get("success"):
        return "## VPC Endpoints\n\n**Error:** Unable to retrieve VPC endpoints"

    data = section_data["data"]
    endpoints = data.get("vpc_endpoints", [])

    md = f"## VPC Endpoints\n\n**Total VPC Endpoints:** {data['total_count']}\n\n"

    if not endpoints:
        md += "*No VPC endpoints found*\n"
        return md

    md += "| Endpoint ID | Name | Type | Service | State |\n"
    md += "|-------------|------|------|---------|-------|\n"

    for ep in endpoints:
        service_name = ep.get("service_name", "-")
        md += f"| {ep['vpc_endpoint_id']} | "
        md += f"{ep.get('name', '<No Name>')} | "
        md += f"{ep['vpc_endpoint_type']} | "
        md += f"{service_name} | "
        md += f"{ep['state']} |\n"

    return md


def _generate_vpc_peering_section(section_data: dict[str, Any]) -> str:
    """Generate VPC Peering section."""
    if not section_data.get("success"):
        return "## VPC Peering Connections\n\n**Error:** Unable to retrieve VPC peering connections"

    data = section_data["data"]
    peerings = data.get("peering_connections", [])  # Fixed: was vpc_peering_connections

    md = f"## VPC Peering Connections\n\n**Total Peering Connections:** {data['total_count']}\n\n"

    if not peerings:
        md += "*No VPC peering connections found*\n"
        return md

    md += "| Peering ID | Name | Requester VPC | Accepter VPC | Status | Cross-Account | Cross-Region |\n"
    md += "|------------|------|---------------|--------------|--------|---------------|---------------|\n"

    for peer in peerings:
        md += f"| {peer['vpc_peering_connection_id']} | "
        md += f"{peer.get('name', 'N/A')} | "
        md += f"{peer['requester_vpc']['vpc_id']} ({peer['requester_vpc']['region']}) | "
        md += f"{peer['accepter_vpc']['vpc_id']} ({peer['accepter_vpc']['region']}) | "
        md += f"{peer['status_code']} | "
        md += f"{'Yes' if peer['is_cross_account'] else 'No'} | "
        md += f"{'Yes' if peer['is_cross_region'] else 'No'} |\n"

    return md


def _generate_transit_gateway_section(section_data: dict[str, Any]) -> str:
    """Generate Transit Gateway Attachments section."""
    if not section_data.get("success"):
        return "## Transit Gateway Attachments\n\n**Error:** Unable to retrieve Transit Gateway attachments"

    data = section_data["data"]
    attachments = data.get("transit_gateway_attachments", [])

    md = f"## Transit Gateway Attachments\n\n**Total Attachments:** {data['total_count']}\n\n"

    if not attachments:
        md += "*No Transit Gateway attachments found*\n"
        return md

    md += "| Attachment ID | Name | TGW ID | State | DNS Support | IPv6 Support |\n"
    md += "|---------------|------|--------|-------|-------------|-------------|\n"

    for att in attachments:
        md += f"| {att['transit_gateway_attachment_id']} | "
        md += f"{att.get('name', '<No Name>')} | "
        md += f"{att['transit_gateway_id']} | "
        md += f"{att['state']} | "
        md += f"{att['dns_support']} | "
        md += f"{att['ipv6_support']} |\n"

    return md


def _generate_vpn_connections_section(section_data: dict[str, Any]) -> str:
    """Generate VPN Connections section."""
    if not section_data.get("success"):
        return "## VPN Connections\n\n**Error:** Unable to retrieve VPN connections"

    data = section_data["data"]
    vpns = data.get("vpn_connections", [])

    md = f"## VPN Connections\n\n**Total VPN Connections:** {data['total_count']}\n\n"

    if not vpns:
        md += "*No VPN connections found*\n"
        return md

    md += "| VPN ID | Name | State | Gateway Type | Gateway ID | Tunnels UP | Tunnels DOWN |\n"
    md += "|--------|------|-------|--------------|------------|------------|-------------|\n"

    for vpn in vpns:
        md += f"| {vpn['vpn_connection_id']} | "
        md += f"{vpn.get('name', '<No Name>')} | "
        md += f"{vpn['state']} | "
        md += f"{vpn['gateway_type']} | "
        md += f"{vpn.get('gateway_id', '-')} | "
        md += f"{vpn['tunnels_up']} | "
        md += f"{vpn['tunnels_down']} |\n"

    # Detailed tunnel information
    md += "\n### VPN Tunnel Details\n\n"
    for vpn in vpns:
        if vpn.get("vgw_telemetry"):
            md += f"#### {vpn['vpn_connection_id']} - {vpn.get('name', '<No Name>')}\n\n"
            md += "| Outside IP | Status | Last Status Change | Accepted Routes |\n"
            md += "|------------|--------|-------------------|----------------|\n"
            for tunnel in vpn["vgw_telemetry"]:
                md += f"| {tunnel.get('outside_ip_address', '-')} | "
                md += f"{tunnel.get('status', 'unknown')} | "
                md += f"{tunnel.get('last_status_change', '-')} | "
                md += f"{tunnel.get('accepted_route_count', 0)} |\n"
            md += "\n"

    return md


def _generate_customer_gateways_section(section_data: dict[str, Any]) -> str:
    """Generate Customer Gateways section."""
    if not section_data.get("success"):
        return "## Customer Gateways\n\n**Error:** Unable to retrieve customer gateways"

    data = section_data["data"]
    cgws = data.get("customer_gateways", [])

    md = f"## Customer Gateways\n\n**Total Customer Gateways:** {data['total_count']}\n\n"

    if not cgws:
        md += "*No customer gateways found*\n"
        return md

    md += "| CGW ID | Name | IP Address | BGP ASN | Type | State |\n"
    md += "|--------|------|------------|---------|------|-------|\n"

    for cgw in cgws:
        md += f"| {cgw['customer_gateway_id']} | "
        md += f"{cgw.get('name', '<No Name>')} | "
        md += f"{cgw.get('ip_address', '-')} | "
        md += f"{cgw.get('bgp_asn', '-')} | "
        md += f"{cgw.get('type', 'ipsec.1')} | "
        md += f"{cgw['state']} |\n"

    return md


def _generate_vpn_gateways_section(section_data: dict[str, Any]) -> str:
    """Generate VPN Gateways section."""
    if not section_data.get("success"):
        return "## VPN Gateways\n\n**Error:** Unable to retrieve VPN gateways"

    data = section_data["data"]
    vgws = data.get("vpn_gateways", [])

    md = f"## VPN Gateways\n\n**Total VPN Gateways:** {data['total_count']}\n\n"

    if not vgws:
        md += "*No VPN gateways found*\n"
        return md

    md += "| VGW ID | Name | Type | State | Amazon Side ASN |\n"
    md += "|--------|------|------|-------|----------------|\n"

    for vgw in vgws:
        md += f"| {vgw['vpn_gateway_id']} | "
        md += f"{vgw.get('name', '<No Name>')} | "
        md += f"{vgw.get('type', 'ipsec.1')} | "
        md += f"{vgw['attachment_state']} | "
        md += f"{vgw.get('amazon_side_asn', '-')} |\n"

    return md


def _generate_dhcp_options_section(section_data: dict[str, Any]) -> str:
    """Generate DHCP Options section."""
    if not section_data.get("success"):
        return "## DHCP Options\n\n**Error:** Unable to retrieve DHCP options"

    data = section_data["data"]
    dhcp_id = data.get("dhcp_options_id")

    md = "## DHCP Options\n\n"

    if not dhcp_id:
        md += "*No DHCP options configured*\n"
        return md

    md += f"### {dhcp_id} - {data.get('name', '<No Name>')}\n\n"
    configs = data.get("configurations", {})
    if configs:
        md += "| Configuration Key | Values |\n"
        md += "|------------------|--------|\n"
        for key, values in configs.items():
            md += f"| {key} | {', '.join(values)} |\n"
        md += "\n"
    else:
        md += "*No DHCP configurations*\n\n"

    return md


def _generate_flow_logs_section(section_data: dict[str, Any]) -> str:
    """Generate VPC Flow Logs section."""
    if not section_data.get("success"):
        return "## VPC Flow Logs\n\n**Error:** Unable to retrieve flow logs"

    data = section_data["data"]
    flow_logs = data.get("flow_logs", [])

    md = f"## VPC Flow Logs\n\n**Total Flow Logs:** {data['total_count']}\n\n"

    if not flow_logs:
        md += "*No flow logs found*\n"
        return md

    md += "| Flow Log ID | Name | Traffic Type | Destination Type | Status |\n"
    md += "|-------------|------|--------------|------------------|--------|\n"

    for log in flow_logs:
        md += f"| {log['flow_log_id']} | "
        md += f"{log.get('name', '<No Name>')} | "
        md += f"{log.get('traffic_type', 'ALL')} | "
        md += f"{log.get('log_destination_type', 'cloud-watch-logs')} | "
        md += f"{log['flow_log_status']} |\n"

    return md


def _generate_network_interfaces_section(section_data: dict[str, Any]) -> str:
    """Generate Network Interfaces section."""
    if not section_data.get("success"):
        return "## Network Interfaces\n\n**Error:** Unable to retrieve network interfaces"

    data = section_data["data"]
    enis = data.get("network_interfaces", [])

    md = f"## Network Interfaces\n\n**Total Network Interfaces:** {data['total_count']}  \n"
    md += f"**AWS-Managed:** {data.get('aws_managed_count', 0)}  \n"
    md += f"**User-Managed:** {data.get('user_managed_count', 0)}\n\n"

    if not enis:
        md += "*No network interfaces found*\n"
        return md

    # Summary by interface type
    type_counts = data.get("interface_type_counts", {})
    if type_counts:
        md += "### Interface Type Summary\n\n"
        md += "| Interface Type | Count |\n"
        md += "|----------------|------:|\n"
        for itype, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            md += f"| {itype} | {count} |\n"
        md += "\n"

    # Detailed table
    md += "### Network Interface Details\n\n"
    md += "| ENI ID | Type | Status | Private IP | Attached To | Description |\n"
    md += "|--------|------|--------|------------|-------------|-------------|\n"

    for eni in enis:
        description = eni.get('description') or '-'
        md += f"| {eni['network_interface_id']} | "
        md += f"{eni['interface_type']} | "
        md += f"{eni['status']} | "
        md += f"{eni.get('private_ip_address', '-')} | "
        md += f"{eni.get('attached_to', '-')} | "
        md += f"{description[:50]} |\n"

    return md


def _generate_vpc_attributes_section(section_data: dict[str, Any]) -> str:
    """Generate VPC Attributes section."""
    if not section_data.get("success"):
        return "## VPC Attributes\n\n**Error:** Unable to retrieve VPC attributes"

    data = section_data["data"]
    attrs = data.get("attributes", {})

    md = "## VPC Attributes\n\n"
    md += "| Attribute | Value |\n"
    md += "|-----------|-------|\n"
    md += f"| DNS Support | {'Enabled' if attrs.get('enable_dns_support') else 'Disabled'} |\n"
    md += f"| DNS Hostnames | {'Enabled' if attrs.get('enable_dns_hostnames') else 'Disabled'} |\n"
    md += f"| Network Address Usage Metrics | {'Enabled' if attrs.get('enable_network_address_usage_metrics') else 'Disabled'} |\n"

    return md


def _generate_direct_connect_vifs_section(section_data: dict[str, Any]) -> str:
    """Generate Direct Connect Virtual Interfaces section."""
    if not section_data.get("success"):
        return "## Direct Connect Virtual Interfaces\n\n**Error:** Unable to retrieve Direct Connect VIFs"

    data = section_data["data"]
    vifs = data.get("virtual_interfaces", [])

    md = f"## Direct Connect Virtual Interfaces\n\n**Total Virtual Interfaces:** {data['total_count']}\n\n"

    if not vifs:
        md += "*No Direct Connect virtual interfaces found*\n"
        return md

    md += "| VIF ID | Name | Type | State | BGP Sessions UP | BGP Sessions DOWN |\n"
    md += "|--------|------|------|-------|-----------------|------------------|\n"

    for vif in vifs:
        md += f"| {vif['virtual_interface_id']} | "
        md += f"{vif.get('name', '<No Name>')} | "
        md += f"{vif.get('virtual_interface_type', '-')} | "
        md += f"{vif['virtual_interface_state']} | "
        md += f"{vif['bgp_sessions_up']} | "
        md += f"{vif['bgp_sessions_down']} |\n"

    # Detailed BGP peer information
    md += "\n### BGP Peer Details\n\n"
    for vif in vifs:
        if vif.get("bgp_peers"):
            md += f"#### {vif['virtual_interface_id']} - {vif.get('name', '<No Name>')}\n\n"
            md += "| BGP Peer IP | BGP Status | BGP Peer State | ASN | Address Family |\n"
            md += "|-------------|------------|----------------|-----|----------------|\n"
            for peer in vif["bgp_peers"]:
                md += f"| {peer.get('bgp_peer_address', '-')} | "
                md += f"{peer.get('bgp_status', 'unknown')} | "
                md += f"{peer.get('bgp_peer_state', '-')} | "
                md += f"{peer.get('asn', '-')} | "
                md += f"{peer.get('address_family', '-')} |\n"
            md += "\n"

    return md


def _generate_footer() -> str:
    """Generate report footer."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")
    return f"""---

**Report generated at:** {timestamp}
**Generated by:** VPC Reporter v0.1.0"""
