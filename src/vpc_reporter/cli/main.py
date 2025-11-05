"""Main CLI entry point for VPC Reporter."""

from __future__ import annotations

import sys

import click
from rich.console import Console

from vpc_reporter import __version__


# Global console instance
console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="awsvpc")
@click.option(
    "--profile",
    envvar="AWS_PROFILE",
    help="AWS profile name to use",
    default="default",
    show_default=True,
)
@click.option(
    "--region",
    envvar="AWS_REGION",
    help="AWS region",
    type=click.Choice(["us-east-1", "sa-east-1", "ap-southeast-1"]),
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
@click.option(
    "--config",
    type=click.Path(exists=True),
    help="Path to configuration file",
)
@click.pass_context
def cli(
    ctx: click.Context,
    profile: str,
    region: str | None,
    verbose: bool,
    config: str | None,
) -> None:
    """AWS VPC Network Reporter - Comprehensive VPC documentation tool.

    Generate detailed reports of your AWS VPC network infrastructure including
    subnets, route tables, security groups, and all network components.
    """
    # Ensure context object exists
    ctx.ensure_object(dict)

    # Store global options in context
    ctx.obj["console"] = console
    ctx.obj["profile"] = profile
    ctx.obj["region"] = region
    ctx.obj["verbose"] = verbose
    ctx.obj["config"] = config

    # Configure logging based on verbose flag
    if verbose:
        console.print("[dim]Verbose mode enabled[/dim]")


@cli.command()
@click.option(
    "--vpc-id",
    help="VPC ID to document (e.g., vpc-0abc123)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path",
)
@click.option(
    "--format",
    type=click.Choice(["markdown", "json", "yaml", "console"]),
    default="markdown",
    help="Output format",
)
@click.option(
    "--sections",
    help="Comma-separated list of sections to include (default: all)",
)
@click.option(
    "--async",
    "use_async",
    is_flag=True,
    help="Use async operations for faster execution",
)
@click.option(
    "--no-cache",
    is_flag=True,
    help="Disable caching of AWS API responses",
)
@click.pass_context
def report(
    ctx: click.Context,
    vpc_id: str | None,
    output: str | None,
    format: str,
    sections: str | None,
    use_async: bool,
    no_cache: bool,
) -> None:
    """Generate a comprehensive VPC network report.

    Examples:
        awsvpc report --vpc-id vpc-0abc123
        awsvpc report --vpc-id vpc-0abc123 --format json
        awsvpc report --vpc-id vpc-0abc123 --async --sections subnets,security-groups
    """
    console = ctx.obj["console"]
    profile = ctx.obj["profile"]
    region = ctx.obj["region"]

    # Import here to avoid circular imports
    from vpc_reporter.cli.report_command import execute_report

    try:
        execute_report(
            console=console,
            profile=profile,
            region=region,
            vpc_id=vpc_id,
            output=output,
            format=format,
            sections=sections,
            use_async=use_async,
            no_cache=no_cache,
        )
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if ctx.obj.get("verbose"):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.pass_context
def list_vpcs(ctx: click.Context) -> None:
    """List all VPCs in the selected region."""
    console = ctx.obj["console"]
    profile = ctx.obj["profile"]
    region = ctx.obj["region"]

    from vpc_reporter.cli.list_command import execute_list_vpcs

    try:
        execute_list_vpcs(
            console=console,
            profile=profile,
            region=region,
        )
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if ctx.obj.get("verbose"):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.option(
    "--init",
    is_flag=True,
    help="Create default configuration file",
)
@click.option(
    "--show",
    is_flag=True,
    help="Show current configuration",
)
@click.option(
    "--path",
    type=click.Path(),
    help="Path to configuration file",
)
@click.pass_context
def config(ctx: click.Context, init: bool, show: bool, path: str | None) -> None:
    """Manage vpc-reporter configuration.

    Examples:
        awsvpc config --init
        awsvpc config --show
        awsvpc config --path ~/.vpc-reporter/config.yaml --show
    """
    console = ctx.obj["console"]

    from vpc_reporter.config.config import ConfigManager, create_default_config

    try:
        if init:
            create_default_config(path)
        elif show:
            config_mgr = ConfigManager(path)
            console.print("\n[bold]Current Configuration:[/bold]\n")
            console.print(f"[cyan]AWS Profile:[/cyan] {config_mgr.get_aws_profile()}")
            console.print(
                f"[cyan]Default Region:[/cyan] {config_mgr.get_default_region()}"
            )
            console.print(
                f"[cyan]Available Regions:[/cyan] {', '.join(config_mgr.get_regions())}"
            )
            console.print(
                f"[cyan]Output Format:[/cyan] {config_mgr.get_output_format()}"
            )
            console.print(
                f"[cyan]Output Directory:[/cyan] {config_mgr.get_output_directory()}"
            )
            console.print(
                f"[cyan]Cache Enabled:[/cyan] {config_mgr.is_cache_enabled()}"
            )
            console.print(f"[cyan]Cache TTL:[/cyan] {config_mgr.get_cache_ttl()}s")
            console.print(
                f"[cyan]Cache Directory:[/cyan] {config_mgr.get_cache_directory()}\n"
            )
        else:
            console.print(
                "[yellow]Use --init to create config or --show to view current config[/yellow]"
            )
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if ctx.obj.get("verbose"):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.option(
    "--vpc-id",
    help="VPC ID to generate diagram for",
)
@click.option(
    "--output",
    type=click.Path(),
    help="Output file for diagram code",
)
@click.option(
    "--style",
    type=click.Choice(["simple", "comprehensive"], case_sensitive=False),
    default="simple",
    help="Diagram style: simple (basic overview) or comprehensive (all resources)",
)
@click.pass_context
def diagram(
    ctx: click.Context, vpc_id: str | None, output: str | None, style: str
) -> None:
    """Generate VPC network diagram code.

    Examples:
        awsvpc diagram --vpc-id vpc-123
        awsvpc diagram --vpc-id vpc-123 --output diagram.py
        awsvpc diagram --vpc-id vpc-123 --style comprehensive --output detailed.py
    """
    console = ctx.obj["console"]
    profile = ctx.obj["profile"]
    region = ctx.obj["region"]

    from vpc_reporter.aws.client import AWSClient
    from vpc_reporter.diagrams.comprehensive_generator import (
        ComprehensiveDiagramGenerator,
    )
    from vpc_reporter.diagrams.generator import DiagramGenerator
    from vpc_reporter.operations.sync_collector import collect_all_data_sync

    try:
        # Get VPC ID if not provided
        if not vpc_id:
            # TODO: Implement interactive VPC selection
            console.print("[red]Error: VPC ID is required. Please use --vpc-id parameter.[/red]")
            return

        console.print(f"\n[bold]Generating {style} diagram for VPC:[/bold] {vpc_id}\n")

        # Collect VPC data
        with console.status("[bold green]Collecting VPC data..."):
            aws_client = AWSClient(profile=profile, region=region)
            vpc_data = collect_all_data_sync(aws_client, vpc_id, progress=None)

        # Generate diagram code based on style
        if style == "comprehensive":
            generator = ComprehensiveDiagramGenerator()
            diagram_code = generator.generate_diagram_code(vpc_data)
            console.print("[cyan]ℹ Comprehensive diagram includes:[/cyan]")
            console.print("  • All subnets grouped by AZ and type (public/private)")
            console.print("  • Route tables with route counts")
            console.print("  • Security groups (top 10) and Network ACLs")
            console.print("  • NAT Gateways, VPC Endpoints, VPN connections")
            console.print("  • Transit Gateway, VPC Peering, and network flows")
        else:
            simple_generator = DiagramGenerator()
            diagram_code = simple_generator.generate_vpc_diagram(vpc_data)

        # Save or display
        if output:
            with open(output, "w") as f:
                f.write(diagram_code)
            console.print(f"\n[green]✓ Diagram code saved to:[/green] {output}")
            console.print(
                f"\n[cyan]To generate the diagram, run:[/cyan] uv run python {output}"
            )
            console.print(f"[dim]Or with system Python:[/dim] python3 {output}")
        else:
            console.print("\n[bold]Generated Diagram Code:[/bold]\n")
            console.print(f"[dim]{diagram_code}[/dim]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if ctx.obj.get("verbose"):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.option(
    "--vpc-id",
    help="VPC ID to analyze costs for",
)
@click.pass_context
def cost(ctx: click.Context, vpc_id: str | None) -> None:
    """Analyze VPC costs.

    Examples:
        awsvpc cost --vpc-id vpc-123
    """
    console = ctx.obj["console"]
    profile = ctx.obj["profile"]
    region = ctx.obj["region"]

    from rich.table import Table

    from vpc_reporter.aws.client import AWSClient
    from vpc_reporter.cost.analyzer import CostAnalyzer
    from vpc_reporter.operations.sync_collector import collect_all_data_sync

    try:
        # Get VPC ID if not provided
        if not vpc_id:
            # TODO: Implement interactive VPC selection
            console.print("[red]Error: VPC ID is required. Please use --vpc-id parameter.[/red]")
            return

        console.print(f"\n[bold]Analyzing costs for VPC:[/bold] {vpc_id}\n")

        # Collect VPC data
        with console.status("[bold green]Collecting VPC data..."):
            aws_client = AWSClient(profile=profile, region=region)
            vpc_data = collect_all_data_sync(aws_client, vpc_id, progress=None)

        # Analyze costs
        analyzer = CostAnalyzer(region=region)
        cost_breakdown = analyzer.analyze_vpc_costs(vpc_data)

        # Display cost breakdown
        table = Table(title=f"VPC Cost Analysis - {vpc_id}")
        table.add_column("Resource", style="cyan")
        table.add_column("Monthly Cost", style="green", justify="right")
        table.add_column("Description", style="dim")

        for driver in cost_breakdown["cost_drivers"]:
            table.add_row(
                driver["resource"],
                f"${driver['monthly_cost']:.2f}",
                driver["description"],
            )

        console.print(table)
        console.print(
            f"\n[bold]Total Monthly Cost:[/bold] [green]${cost_breakdown['total_monthly_cost']:.2f}[/green]\n"
        )

        # Display recommendations
        recommendations = analyzer.generate_cost_recommendations(cost_breakdown)
        if recommendations:
            console.print("[bold]💡 Cost Optimization Recommendations:[/bold]\n")
            for i, rec in enumerate(recommendations, 1):
                console.print(f"  {i}. {rec}")
            console.print()

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if ctx.obj.get("verbose"):
            console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    cli()
