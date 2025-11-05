"""Report command implementation."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from vpc_reporter.aws.client import AWSClient
from vpc_reporter.operations.vpc_ops import VPCOperations


def execute_report(
    console: Console,
    profile: str,
    region: str | None,
    vpc_id: str | None,
    output: str | None,
    format: str,
    sections: str | None,
    use_async: bool,
    no_cache: bool,
) -> None:
    """Execute the report generation."""

    # Interactive region selection if not provided
    if not region:
        region = _select_region_interactive(console)

    # Interactive VPC selection if not provided
    if not vpc_id:
        vpc_id = _select_vpc_interactive(console, profile, region)

    console.print(Panel(
        f"[bold cyan]Profile:[/] {profile}\n"
        f"[bold cyan]Region:[/] {region}\n"
        f"[bold cyan]VPC ID:[/] {vpc_id}\n"
        f"[bold cyan]Format:[/] {format}\n"
        f"[bold cyan]Async:[/] {'Yes' if use_async else 'No'}",
        title="[bold]Report Configuration[/bold]",
        border_style="green"
    ))

    # Initialize AWS client
    aws_client = AWSClient(profile=profile, region=region, use_cache=not no_cache)

    # Parse sections filter
    selected_sections = None
    if sections:
        selected_sections = [s.strip() for s in sections.split(",")]

    # Generate report
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Gathering VPC data...", total=None)

        if use_async:
            import asyncio

            from vpc_reporter.operations.async_collector import collect_all_data_async
            data = asyncio.run(collect_all_data_async(
                aws_client=aws_client,
                vpc_id=vpc_id,
                sections=selected_sections,
            ))
        else:
            from vpc_reporter.operations.sync_collector import collect_all_data_sync
            data = collect_all_data_sync(
                aws_client=aws_client,
                vpc_id=vpc_id,
                sections=selected_sections,
                progress=progress,
            )

        progress.update(task, description="[green]Data collection complete!")

    # Generate output
    if format == "console":
        from vpc_reporter.output.console import render_console_output
        render_console_output(console, data)
    elif format == "markdown":
        from vpc_reporter.output.markdown import generate_markdown
        content = generate_markdown(data)
        if output:
            Path(output).write_text(content)
            console.print(f"[green]✓[/green] Report saved to: {output}")
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"vpc-network-report-{timestamp}.md"
            Path(output_path).write_text(content)
            console.print(f"[green]✓[/green] Report saved to: {output_path}")
    elif format == "json":
        from vpc_reporter.output.json_output import generate_json
        content = generate_json(data)
        if output:
            Path(output).write_text(content)
            console.print(f"[green]✓[/green] Report saved to: {output}")
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"vpc-network-report-{timestamp}.json"
            Path(output_path).write_text(content)
            console.print(f"[green]✓[/green] Report saved to: {output_path}")
    elif format == "yaml":
        from vpc_reporter.output.yaml_output import generate_yaml
        content = generate_yaml(data)
        if output:
            Path(output).write_text(content)
            console.print(f"[green]✓[/green] Report saved to: {output}")
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"vpc-network-report-{timestamp}.yaml"
            Path(output_path).write_text(content)
            console.print(f"[green]✓[/green] Report saved to: {output_path}")


def _select_region_interactive(console: Console) -> str:
    """Interactive region selection."""
    console.print("\n[bold]Select AWS Region:[/bold]")
    console.print("1) us-east-1 (N. Virginia)")
    console.print("2) sa-east-1 (São Paulo)")
    console.print("3) ap-southeast-1 (Singapore)")

    choice = console.input("\nEnter your choice (1-3): ")

    region_map = {
        "1": "us-east-1",
        "2": "sa-east-1",
        "3": "ap-southeast-1",
    }

    region = region_map.get(choice)
    if not region:
        console.print("[red]Invalid choice. Using us-east-1[/red]")
        return "us-east-1"

    console.print(f"[green]✓[/green] Selected region: {region}\n")
    return region


def _select_vpc_interactive(console: Console, profile: str, region: str) -> str:
    """Interactive VPC selection."""

    console.print("[cyan]Fetching VPCs...[/cyan]")

    aws_client = AWSClient(profile=profile, region=region)
    vpc_ops = VPCOperations(aws_client)

    vpcs = vpc_ops.list_vpcs()

    if not vpcs:
        console.print("[red]No VPCs found in region {region}[/red]")
        raise ValueError(f"No VPCs found in region {region}")

    console.print("\n[bold]Available VPCs:[/bold]")
    for idx, vpc in enumerate(vpcs, 1):
        name = vpc.get("name", "<No Name>")
        vpc_id = vpc["vpc_id"]
        cidr = vpc["cidr_block"]
        console.print(f"{idx}) {vpc_id} | {cidr} | {name}")

    choice = console.input("\nEnter VPC number or VPC ID directly: ")

    # Check if input is a number (selection) or VPC ID
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(vpcs):
            vpc_id = vpcs[idx]["vpc_id"]
        else:
            console.print("[red]Invalid selection[/red]")
            raise ValueError("Invalid VPC selection")
    elif choice.startswith("vpc-"):
        vpc_id = choice
    else:
        console.print("[red]Invalid input[/red]")
        raise ValueError("Invalid VPC input")

    console.print(f"[green]✓[/green] Selected VPC: {vpc_id}\n")
    return vpc_id
