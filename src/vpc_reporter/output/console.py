"""Rich console output renderer."""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table


def render_console_output(console: Console, data: dict[str, Any]) -> None:
    """Render VPC data to Rich console.

    Args:
        console: Rich console instance
        data: Collected VPC data
    """
    vpc_id = data.get("vpc_id", "Unknown")
    region = data.get("region", "Unknown")
    sections = data.get("sections", {})

    # Header
    console.print(Panel(
        f"[bold cyan]VPC ID:[/] {vpc_id}\n"
        f"[bold cyan]Region:[/] {region}\n"
        f"[bold cyan]Sections:[/] {len(sections)}",
        title="[bold]VPC Network Report[/bold]",
        border_style="green"
    ))

    # VPC Overview
    if "vpc" in sections:
        _render_vpc_section(console, sections["vpc"])

    # Subnets
    if "subnets" in sections:
        _render_subnets_section(console, sections["subnets"])

    # Route Tables
    if "route_tables" in sections:
        _render_route_tables_section(console, sections["route_tables"])

    # Security Groups
    if "security_groups" in sections:
        _render_security_groups_section(console, sections["security_groups"])

    # Network ACLs
    if "network_acls" in sections:
        _render_network_acls_section(console, sections["network_acls"])

    # Internet Gateways
    if "internet_gateways" in sections:
        _render_internet_gateways_section(console, sections["internet_gateways"])

    # NAT Gateways
    if "nat_gateways" in sections:
        _render_nat_gateways_section(console, sections["nat_gateways"])

    # Elastic IPs
    if "elastic_ips" in sections:
        _render_elastic_ips_section(console, sections["elastic_ips"])

    # VPC Endpoints
    if "vpc_endpoints" in sections:
        _render_vpc_endpoints_section(console, sections["vpc_endpoints"])

    # VPC Peering
    if "vpc_peering" in sections:
        _render_vpc_peering_section(console, sections["vpc_peering"])

    # Transit Gateway Attachments
    if "transit_gateway_attachments" in sections:
        _render_transit_gateway_section(console, sections["transit_gateway_attachments"])

    # VPN Connections
    if "vpn_connections" in sections:
        _render_vpn_connections_section(console, sections["vpn_connections"])

    # Customer Gateways
    if "customer_gateways" in sections:
        _render_customer_gateways_section(console, sections["customer_gateways"])

    # VPN Gateways
    if "vpn_gateways" in sections:
        _render_vpn_gateways_section(console, sections["vpn_gateways"])

    # DHCP Options
    if "dhcp_options" in sections:
        _render_dhcp_options_section(console, sections["dhcp_options"])

    # Flow Logs
    if "flow_logs" in sections:
        _render_flow_logs_section(console, sections["flow_logs"])

    # Network Interfaces
    if "network_interfaces" in sections:
        _render_network_interfaces_section(console, sections["network_interfaces"])

    # VPC Attributes
    if "vpc_attributes" in sections:
        _render_vpc_attributes_section(console, sections["vpc_attributes"])

    # Direct Connect VIFs
    if "direct_connect_vifs" in sections:
        _render_direct_connect_vifs_section(console, sections["direct_connect_vifs"])


def _render_vpc_section(console: Console, section_data: dict[str, Any]) -> None:
    """Render VPC overview section."""
    if not section_data.get("success"):
        console.print("[red]✗ VPC Overview: Error[/red]")
        return

    vpc = section_data["data"]
    console.print("\n[bold]VPC Overview[/bold]")
    console.print(f"  CIDR Block: {vpc['cidr_block']}")
    console.print(f"  State: {vpc['state']}")
    console.print(f"  Name: {vpc.get('name', '<No Name>')}")
    console.print(f"  Tenancy: {vpc.get('instance_tenancy', 'default')}")


def _render_subnets_section(console: Console, section_data: dict[str, Any]) -> None:
    """Render subnets section."""
    if not section_data.get("success"):
        console.print("[red]✗ Subnets: Error[/red]")
        return

    data = section_data["data"]
    subnets = data.get("subnets", [])

    console.print(f"\n[bold]Subnets ({data['total_count']})[/bold]")

    table = Table()
    table.add_column("Subnet ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("CIDR", style="yellow")
    table.add_column("AZ", style="magenta")
    table.add_column("Available IPs", justify="right")
    table.add_column("Public", style="blue")

    for subnet in subnets:
        table.add_row(
            subnet["subnet_id"],
            subnet.get("name", "<No Name>"),
            subnet["cidr_block"],
            subnet["availability_zone"],
            str(subnet["available_ip_count"]),
            "✓" if subnet["map_public_ip"] else "✗",
        )

    console.print(table)


def _render_route_tables_section(console: Console, section_data: dict[str, Any]) -> None:
    """Render route tables section."""
    if not section_data.get("success"):
        console.print("[red]✗ Route Tables: Error[/red]")
        return

    data = section_data["data"]
    route_tables = data.get("route_tables", [])

    console.print(f"\n[bold]Route Tables ({data['total_count']})[/bold]")

    for rt in route_tables:
        rt_type = "Main" if rt["is_main"] else "Custom"
        console.print(f"\n  [cyan]{rt['route_table_id']}[/cyan] - {rt.get('name', '<No Name>')} ({rt_type})")
        console.print(f"    Associated Subnets: {len(rt['associated_subnets'])}")
        console.print(f"    Routes: {len(rt['routes'])}")


def _render_security_groups_section(console: Console, section_data: dict[str, Any]) -> None:
    """Render security groups section."""
    if not section_data.get("success"):
        console.print("[red]✗ Security Groups: Error[/red]")
        return

    data = section_data["data"]
    security_groups = data.get("security_groups", [])

    console.print(f"\n[bold]Security Groups ({data['total_count']})[/bold]")

    # Summary table
    table = Table(title="Security Group Summary")
    table.add_column("Group ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Description")
    table.add_column("Inbound", justify="right")
    table.add_column("Outbound", justify="right")

    for sg in security_groups:
        table.add_row(
            sg["group_id"],
            sg.get("name", sg["group_name"]),
            sg["description"][:50] + "..." if len(sg["description"]) > 50 else sg["description"],
            str(sg["inbound_rules_count"]),
            str(sg["outbound_rules_count"]),
        )

    console.print(table)

    # Detailed rules for each security group
    for sg in security_groups:
        console.print(f"\n[bold cyan]{sg['group_id']}[/bold cyan] - {sg.get('name', sg['group_name'])}")

        # Inbound rules
        if sg["inbound_rules"]:
            console.print("  [bold]Inbound Rules:[/bold]")
            rules_table = Table(show_header=True, box=None, padding=(0, 1))
            rules_table.add_column("Type", style="yellow")
            rules_table.add_column("Protocol", style="magenta")
            rules_table.add_column("Port", style="cyan")
            rules_table.add_column("Source", style="green")
            rules_table.add_column("Description")

            for rule in sg["inbound_rules"][:10]:  # Limit to 10 for console
                rules_table.add_row(
                    rule["type"],
                    rule["protocol"],
                    str(rule["port_range"]),
                    rule["source"][:40] + "..." if len(rule["source"]) > 40 else rule["source"],
                    rule.get("description", "")[:30] + "..." if len(rule.get("description", "")) > 30 else rule.get("description", ""),
                )

            console.print(rules_table)
            if len(sg["inbound_rules"]) > 10:
                console.print(f"  [dim]... and {len(sg['inbound_rules']) - 10} more rules[/dim]")
        else:
            console.print("  [dim]No inbound rules[/dim]")

        # Outbound rules
        if sg["outbound_rules"]:
            console.print("  [bold]Outbound Rules:[/bold]")
            rules_table = Table(show_header=True, box=None, padding=(0, 1))
            rules_table.add_column("Type", style="yellow")
            rules_table.add_column("Protocol", style="magenta")
            rules_table.add_column("Port", style="cyan")
            rules_table.add_column("Destination", style="green")
            rules_table.add_column("Description")

            for rule in sg["outbound_rules"][:10]:  # Limit to 10 for console
                rules_table.add_row(
                    rule["type"],
                    rule["protocol"],
                    str(rule["port_range"]),
                    rule["source"][:40] + "..." if len(rule["source"]) > 40 else rule["source"],
                    rule.get("description", "")[:30] + "..." if len(rule.get("description", "")) > 30 else rule.get("description", ""),
                )

            console.print(rules_table)
            if len(sg["outbound_rules"]) > 10:
                console.print(f"  [dim]... and {len(sg['outbound_rules']) - 10} more rules[/dim]")
        else:
            console.print("  [dim]No outbound rules[/dim]")


def _render_network_acls_section(console: Console, section_data: dict[str, Any]) -> None:
    """Render network ACLs section."""
    if not section_data.get("success"):
        console.print("[red]✗ Network ACLs: Error[/red]")
        return

    data = section_data["data"]
    network_acls = data.get("network_acls", [])

    console.print(f"\n[bold]Network ACLs ({data['total_count']})[/bold]")

    # Summary table
    table = Table(title="Network ACL Summary")
    table.add_column("NACL ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Default", style="blue")
    table.add_column("Subnets", justify="right")
    table.add_column("Inbound", justify="right")
    table.add_column("Outbound", justify="right")

    for nacl in network_acls:
        table.add_row(
            nacl["network_acl_id"],
            nacl.get("name", "<No Name>"),
            "✓" if nacl["is_default"] else "✗",
            str(nacl["associated_subnet_count"]),
            str(nacl["inbound_rules_count"]),
            str(nacl["outbound_rules_count"]),
        )

    console.print(table)

    # Detailed rules for each NACL
    for nacl in network_acls:
        console.print(f"\n[bold cyan]{nacl['network_acl_id']}[/bold cyan] - {nacl.get('name', '<No Name>')}")

        # Inbound rules
        if nacl["inbound_rules"]:
            console.print("  [bold]Inbound Rules:[/bold]")
            rules_table = Table(show_header=True, box=None, padding=(0, 1))
            rules_table.add_column("Rule #", justify="right", style="yellow")
            rules_table.add_column("Action", style="magenta")
            rules_table.add_column("Protocol", style="cyan")
            rules_table.add_column("Port", style="blue")
            rules_table.add_column("Source", style="green")

            for rule in nacl["inbound_rules"][:15]:  # Limit to 15 for console
                action_color = "green" if rule["rule_action"] == "ALLOW" else "red"
                rules_table.add_row(
                    str(rule["rule_number"]),
                    f"[{action_color}]{rule['rule_action']}[/{action_color}]",
                    rule["protocol"],
                    str(rule["port_range"]),
                    rule["cidr_block"][:30] + "..." if len(rule["cidr_block"]) > 30 else rule["cidr_block"],
                )

            console.print(rules_table)
            if len(nacl["inbound_rules"]) > 15:
                console.print(f"  [dim]... and {len(nacl['inbound_rules']) - 15} more rules[/dim]")
        else:
            console.print("  [dim]No inbound rules[/dim]")

        # Outbound rules
        if nacl["outbound_rules"]:
            console.print("  [bold]Outbound Rules:[/bold]")
            rules_table = Table(show_header=True, box=None, padding=(0, 1))
            rules_table.add_column("Rule #", justify="right", style="yellow")
            rules_table.add_column("Action", style="magenta")
            rules_table.add_column("Protocol", style="cyan")
            rules_table.add_column("Port", style="blue")
            rules_table.add_column("Destination", style="green")

            for rule in nacl["outbound_rules"][:15]:  # Limit to 15 for console
                action_color = "green" if rule["rule_action"] == "ALLOW" else "red"
                rules_table.add_row(
                    str(rule["rule_number"]),
                    f"[{action_color}]{rule['rule_action']}[/{action_color}]",
                    rule["protocol"],
                    str(rule["port_range"]),
                    rule["cidr_block"][:30] + "..." if len(rule["cidr_block"]) > 30 else rule["cidr_block"],
                )

            console.print(rules_table)
            if len(nacl["outbound_rules"]) > 15:
                console.print(f"  [dim]... and {len(nacl['outbound_rules']) - 15} more rules[/dim]")
        else:
            console.print("  [dim]No outbound rules[/dim]")


def _render_internet_gateways_section(console: Console, section_data: dict[str, Any]) -> None:
    """Render Internet Gateways section."""
    if not section_data.get("success"):
        console.print("[red]✗ Internet Gateways: Error[/red]")
        return

    data = section_data["data"]
    igws = data.get("internet_gateways", [])

    console.print(f"\n[bold]Internet Gateways ({data['total_count']})[/bold]")

    if not igws:
        console.print("  [dim]No internet gateways found[/dim]")
        return

    table = Table()
    table.add_column("IGW ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("State", style="yellow")
    table.add_column("Owner", style="magenta")

    for igw in igws:
        state_color = "green" if igw["attachment_state"] == "available" else "yellow"
        table.add_row(
            igw["internet_gateway_id"],
            igw.get("name", "<No Name>"),
            f"[{state_color}]{igw['attachment_state']}[/{state_color}]",
            igw["owner_id"],
        )

    console.print(table)


def _render_nat_gateways_section(console: Console, section_data: dict[str, Any]) -> None:
    """Render NAT Gateways section."""
    if not section_data.get("success"):
        console.print("[red]✗ NAT Gateways: Error[/red]")
        return

    data = section_data["data"]
    nat_gws = data.get("nat_gateways", [])

    console.print(f"\n[bold]NAT Gateways ({data['total_count']})[/bold]")

    if not nat_gws:
        console.print("  [dim]No NAT gateways found[/dim]")
        return

    table = Table()
    table.add_column("NAT GW ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("State", style="yellow")
    table.add_column("Subnet", style="magenta")
    table.add_column("Public IP", style="blue")

    for nat in nat_gws:
        state_color = "green" if nat["state"] == "available" else "yellow"
        public_ips = ", ".join([addr["public_ip"] for addr in nat["nat_gateway_addresses"] if addr.get("public_ip")])
        table.add_row(
            nat["nat_gateway_id"],
            nat.get("name", "<No Name>"),
            f"[{state_color}]{nat['state']}[/{state_color}]",
            nat["subnet_id"],
            public_ips[:30] + "..." if len(public_ips) > 30 else public_ips,
        )

    console.print(table)


def _render_elastic_ips_section(console: Console, section_data: dict[str, Any]) -> None:
    """Render Elastic IPs section."""
    if not section_data.get("success"):
        console.print("[red]✗ Elastic IPs: Error[/red]")
        return

    data = section_data["data"]
    eips = data.get("elastic_ips", [])

    console.print(f"\n[bold]Elastic IPs ({data['total_count']})[/bold]")

    if not eips:
        console.print("  [dim]No Elastic IPs found[/dim]")
        return

    table = Table()
    table.add_column("Public IP", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Allocation ID", style="yellow")
    table.add_column("Associated", style="magenta")
    table.add_column("Instance/ENI", style="blue")

    for eip in eips:
        associated = "✓" if eip["is_associated"] else "✗"
        resource = eip.get("instance_id") or eip.get("network_interface_id") or "-"
        table.add_row(
            eip["public_ip"],
            eip.get("name", "<No Name>"),
            eip.get("allocation_id", "-"),
            associated,
            resource[:25] + "..." if len(resource) > 25 else resource,
        )

    console.print(table)


def _render_vpc_endpoints_section(console: Console, section_data: dict[str, Any]) -> None:
    """Render VPC Endpoints section."""
    if not section_data.get("success"):
        console.print("[red]✗ VPC Endpoints: Error[/red]")
        return

    data = section_data["data"]
    endpoints = data.get("vpc_endpoints", [])

    console.print(f"\n[bold]VPC Endpoints ({data['total_count']})[/bold]")

    if not endpoints:
        console.print("  [dim]No VPC endpoints found[/dim]")
        return

    table = Table()
    table.add_column("Endpoint ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("Service", style="magenta")
    table.add_column("State", style="blue")

    for ep in endpoints:
        state_color = "green" if ep["state"] == "available" else "yellow"
        service_name = ep["service_name"].split(".")[-1] if ep.get("service_name") else "-"
        table.add_row(
            ep["vpc_endpoint_id"],
            ep.get("name", "<No Name>"),
            ep["vpc_endpoint_type"],
            service_name,
            f"[{state_color}]{ep['state']}[/{state_color}]",
        )

    console.print(table)


def _render_vpc_peering_section(console: Console, section_data: dict[str, Any]) -> None:
    """Render VPC Peering section."""
    if not section_data.get("success"):
        console.print("[red]✗ VPC Peering: Error[/red]")
        return

    data = section_data["data"]
    peerings = data.get("vpc_peering_connections", [])

    console.print(f"\n[bold]VPC Peering Connections ({data['total_count']})[/bold]")

    if not peerings:
        console.print("  [dim]No VPC peering connections found[/dim]")
        return

    table = Table()
    table.add_column("Peering ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Requester VPC", style="yellow")
    table.add_column("Accepter VPC", style="magenta")
    table.add_column("Status", style="blue")

    for peer in peerings:
        status_color = "green" if peer["status"] == "active" else "yellow"
        table.add_row(
            peer["vpc_peering_connection_id"],
            peer.get("name", "<No Name>"),
            peer["requester_vpc_id"],
            peer["accepter_vpc_id"],
            f"[{status_color}]{peer['status']}[/{status_color}]",
        )

    console.print(table)


def _render_transit_gateway_section(console: Console, section_data: dict[str, Any]) -> None:
    """Render Transit Gateway Attachments section."""
    if not section_data.get("success"):
        console.print("[red]✗ Transit Gateway Attachments: Error[/red]")
        return

    data = section_data["data"]
    attachments = data.get("transit_gateway_attachments", [])

    console.print(f"\n[bold]Transit Gateway Attachments ({data['total_count']})[/bold]")

    if not attachments:
        console.print("  [dim]No Transit Gateway attachments found[/dim]")
        return

    table = Table()
    table.add_column("Attachment ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("TGW ID", style="yellow")
    table.add_column("State", style="magenta")
    table.add_column("DNS/IPv6", style="blue")

    for att in attachments:
        state_color = "green" if att["state"] == "available" else "yellow"
        dns_ipv6 = f"DNS:{att['dns_support']}/IPv6:{att['ipv6_support']}"
        table.add_row(
            att["transit_gateway_attachment_id"],
            att.get("name", "<No Name>"),
            att["transit_gateway_id"],
            f"[{state_color}]{att['state']}[/{state_color}]",
            dns_ipv6,
        )

    console.print(table)


def _render_vpn_connections_section(console: Console, section_data: dict[str, Any]) -> None:
    """Render VPN Connections section."""
    if not section_data.get("success"):
        console.print("[red]✗ VPN Connections: Error[/red]")
        return

    data = section_data["data"]
    vpns = data.get("vpn_connections", [])

    console.print(f"\n[bold]VPN Connections ({data['total_count']})[/bold]")

    if not vpns:
        console.print("  [dim]No VPN connections found[/dim]")
        return

    table = Table()
    table.add_column("VPN ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("State", style="yellow")
    table.add_column("Gateway", style="magenta")
    table.add_column("Tunnels", style="blue")

    for vpn in vpns:
        state_color = "green" if vpn["state"] == "available" else "yellow"
        tunnel_status = f"{vpn['tunnels_up']}↑/{vpn['tunnels_down']}↓"
        tunnel_color = "green" if vpn.get("all_tunnels_up") else "red"
        table.add_row(
            vpn["vpn_connection_id"],
            vpn.get("name", "<No Name>"),
            f"[{state_color}]{vpn['state']}[/{state_color}]",
            vpn.get("gateway_id", "-")[:20],
            f"[{tunnel_color}]{tunnel_status}[/{tunnel_color}]",
        )

    console.print(table)


def _render_customer_gateways_section(console: Console, section_data: dict[str, Any]) -> None:
    """Render Customer Gateways section."""
    if not section_data.get("success"):
        console.print("[red]✗ Customer Gateways: Error[/red]")
        return

    data = section_data["data"]
    cgws = data.get("customer_gateways", [])

    console.print(f"\n[bold]Customer Gateways ({data['total_count']})[/bold]")

    if not cgws:
        console.print("  [dim]No customer gateways found[/dim]")
        return

    table = Table()
    table.add_column("CGW ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("IP Address", style="yellow")
    table.add_column("BGP ASN", style="magenta")
    table.add_column("State", style="blue")

    for cgw in cgws:
        state_color = "green" if cgw["state"] == "available" else "yellow"
        table.add_row(
            cgw["customer_gateway_id"],
            cgw.get("name", "<No Name>"),
            cgw.get("ip_address", "-"),
            str(cgw.get("bgp_asn", "-")),
            f"[{state_color}]{cgw['state']}[/{state_color}]",
        )

    console.print(table)


def _render_vpn_gateways_section(console: Console, section_data: dict[str, Any]) -> None:
    """Render VPN Gateways section."""
    if not section_data.get("success"):
        console.print("[red]✗ VPN Gateways: Error[/red]")
        return

    data = section_data["data"]
    vgws = data.get("vpn_gateways", [])

    console.print(f"\n[bold]VPN Gateways ({data['total_count']})[/bold]")

    if not vgws:
        console.print("  [dim]No VPN gateways found[/dim]")
        return

    table = Table()
    table.add_column("VGW ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("State", style="magenta")
    table.add_column("ASN", style="blue")

    for vgw in vgws:
        state_color = "green" if vgw["attachment_state"] == "attached" else "yellow"
        table.add_row(
            vgw["vpn_gateway_id"],
            vgw.get("name", "<No Name>"),
            vgw.get("type", "ipsec.1"),
            f"[{state_color}]{vgw['attachment_state']}[/{state_color}]",
            str(vgw.get("amazon_side_asn", "-")),
        )

    console.print(table)


def _render_dhcp_options_section(console: Console, section_data: dict[str, Any]) -> None:
    """Render DHCP Options section."""
    if not section_data.get("success"):
        console.print("[red]✗ DHCP Options: Error[/red]")
        return

    data = section_data["data"]
    dhcp_id = data.get("dhcp_options_id")

    console.print("\n[bold]DHCP Options[/bold]")

    if not dhcp_id:
        console.print("  [dim]No DHCP options configured[/dim]")
        return

    console.print(f"\n[bold cyan]{dhcp_id}[/bold cyan] - {data.get('name', '<No Name>')}")
    configs = data.get("configurations", {})
    for key, values in configs.items():
        console.print(f"  {key}: {', '.join(values)}")


def _render_flow_logs_section(console: Console, section_data: dict[str, Any]) -> None:
    """Render VPC Flow Logs section."""
    if not section_data.get("success"):
        console.print("[red]✗ VPC Flow Logs: Error[/red]")
        return

    data = section_data["data"]
    flow_logs = data.get("flow_logs", [])

    console.print(f"\n[bold]VPC Flow Logs ({data['total_count']})[/bold]")

    if not flow_logs:
        console.print("  [dim]No flow logs found[/dim]")
        return

    table = Table()
    table.add_column("Flow Log ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Traffic Type", style="yellow")
    table.add_column("Destination", style="magenta")
    table.add_column("Status", style="blue")

    for log in flow_logs:
        status_color = "green" if log["flow_log_status"] == "ACTIVE" else "yellow"
        dest = log.get("log_destination_type", "cloud-watch-logs")
        table.add_row(
            log["flow_log_id"],
            log.get("name", "<No Name>"),
            log.get("traffic_type", "ALL"),
            dest,
            f"[{status_color}]{log['flow_log_status']}[/{status_color}]",
        )

    console.print(table)


def _render_network_interfaces_section(console: Console, section_data: dict[str, Any]) -> None:
    """Render Network Interfaces section."""
    if not section_data.get("success"):
        console.print("[red]✗ Network Interfaces: Error[/red]")
        return

    data = section_data["data"]
    enis = data.get("network_interfaces", [])

    console.print(f"\n[bold]Network Interfaces ({data['total_count']})[/bold]")
    console.print(f"  AWS-Managed: {data.get('aws_managed_count', 0)} | User-Managed: {data.get('user_managed_count', 0)}")

    if not enis:
        console.print("  [dim]No network interfaces found[/dim]")
        return

    # Show summary by interface type
    type_counts = data.get("interface_type_counts", {})
    if type_counts:
        console.print("\n[bold]By Interface Type:[/bold]")
        for itype, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            console.print(f"  {itype}: {count}")

    # Show detailed table (limit to 20 for console)
    console.print(f"\n[bold]Interface Details (showing {min(20, len(enis))} of {len(enis)}):[/bold]")
    table = Table()
    table.add_column("ENI ID", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Private IP", style="magenta")
    table.add_column("Attached To", style="blue")

    for eni in enis[:20]:
        status_color = "green" if eni["status"] == "in-use" else "yellow"
        attached_to = eni.get("attached_to", "-")
        table.add_row(
            eni["network_interface_id"],
            eni["interface_type"][:15],
            f"[{status_color}]{eni['status']}[/{status_color}]",
            eni.get("private_ip_address", "-"),
            attached_to[:25] + "..." if len(attached_to) > 25 else attached_to,
        )

    console.print(table)
    if len(enis) > 20:
        console.print(f"  [dim]... and {len(enis) - 20} more interfaces[/dim]")


def _render_vpc_attributes_section(console: Console, section_data: dict[str, Any]) -> None:
    """Render VPC Attributes section."""
    if not section_data.get("success"):
        console.print("[red]✗ VPC Attributes: Error[/red]")
        return

    data = section_data["data"]
    attrs = data.get("attributes", {})

    console.print("\n[bold]VPC Attributes[/bold]")
    console.print(f"  DNS Support: {'✓' if attrs.get('enable_dns_support') else '✗'}")
    console.print(f"  DNS Hostnames: {'✓' if attrs.get('enable_dns_hostnames') else '✗'}")
    console.print(f"  Network Address Usage Metrics: {'✓' if attrs.get('enable_network_address_usage_metrics') else '✗'}")


def _render_direct_connect_vifs_section(console: Console, section_data: dict[str, Any]) -> None:
    """Render Direct Connect Virtual Interfaces section."""
    if not section_data.get("success"):
        console.print("[red]✗ Direct Connect VIFs: Error[/red]")
        return

    data = section_data["data"]
    vifs = data.get("virtual_interfaces", [])

    console.print(f"\n[bold]Direct Connect Virtual Interfaces ({data['total_count']})[/bold]")

    if not vifs:
        console.print("  [dim]No Direct Connect virtual interfaces found[/dim]")
        return

    table = Table()
    table.add_column("VIF ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("State", style="magenta")
    table.add_column("BGP Status", style="blue")

    for vif in vifs:
        state_color = "green" if vif["virtual_interface_state"] == "available" else "yellow"
        bgp_status = f"{vif['bgp_sessions_up']}↑/{vif['bgp_sessions_down']}↓"
        bgp_color = "green" if vif.get("all_bgp_sessions_up") else "red"
        table.add_row(
            vif["virtual_interface_id"],
            vif.get("name", "<No Name>"),
            vif.get("virtual_interface_type", "-"),
            f"[{state_color}]{vif['virtual_interface_state']}[/{state_color}]",
            f"[{bgp_color}]{bgp_status}[/{bgp_color}]",
        )

    console.print(table)
