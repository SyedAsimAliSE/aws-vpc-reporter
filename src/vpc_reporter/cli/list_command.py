"""List VPCs command implementation."""

from __future__ import annotations

from rich.console import Console
from rich.table import Table

from vpc_reporter.aws.client import AWSClient
from vpc_reporter.operations.vpc_ops import VPCOperations


def execute_list_vpcs(
    console: Console,
    profile: str,
    region: str | None,
) -> None:
    """List all VPCs in the region."""

    if not region:
        from vpc_reporter.cli.report_command import _select_region_interactive

        region = _select_region_interactive(console)

    console.print(f"[cyan]Fetching VPCs in {region}...[/cyan]\n")

    aws_client = AWSClient(profile=profile, region=region)
    vpc_ops = VPCOperations(aws_client)

    vpcs = vpc_ops.list_vpcs()

    if not vpcs:
        console.print(f"[yellow]No VPCs found in region {region}[/yellow]")
        return

    # Create table
    table = Table(title=f"VPCs in {region}")
    table.add_column("VPC ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="green")
    table.add_column("CIDR Block", style="yellow")
    table.add_column("State", style="magenta")
    table.add_column("Default", style="blue")

    for vpc in vpcs:
        table.add_row(
            vpc["vpc_id"],
            vpc.get("name", "<No Name>"),
            vpc["cidr_block"],
            vpc["state"],
            "✓" if vpc.get("is_default", False) else "✗",
        )

    console.print(table)
    console.print(f"\n[bold]Total VPCs:[/bold] {len(vpcs)}")
