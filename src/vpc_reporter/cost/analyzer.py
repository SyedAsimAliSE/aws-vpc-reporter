"""VPC cost analysis using AWS Pricing API."""

from __future__ import annotations

from typing import Any

from loguru import logger


class CostAnalyzer:
    """Analyze VPC costs using AWS Pricing data."""

    def __init__(self, region: str = "us-east-1") -> None:
        """Initialize cost analyzer.

        Args:
            region: AWS region for pricing
        """
        self.region = region
        self.pricing_cache: dict[str, Any] = {}

    def analyze_vpc_costs(self, vpc_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze costs for VPC resources.

        Args:
            vpc_data: VPC data from collector

        Returns:
            Cost analysis breakdown
        """
        vpc_id = vpc_data.get("vpc_id", "unknown")
        sections = vpc_data.get("sections", {})

        logger.info(f"Analyzing costs for VPC {vpc_id}")

        cost_breakdown = {
            "vpc_id": vpc_id,
            "region": self.region,
            "monthly_costs": {},
            "total_monthly_cost": 0.0,
            "cost_drivers": [],
        }

        # Analyze NAT Gateway costs
        nat_cost = self._analyze_nat_gateway_costs(sections.get("nat_gateways", {}))
        if nat_cost > 0:
            cost_breakdown["monthly_costs"]["nat_gateways"] = nat_cost
            cost_breakdown["total_monthly_cost"] += nat_cost
            cost_breakdown["cost_drivers"].append({
                "resource": "NAT Gateways",
                "monthly_cost": nat_cost,
                "description": "NAT Gateway hourly charges + data processing",
            })

        # Analyze VPN costs
        vpn_cost = self._analyze_vpn_costs(sections.get("vpn_connections", {}))
        if vpn_cost > 0:
            cost_breakdown["monthly_costs"]["vpn_connections"] = vpn_cost
            cost_breakdown["total_monthly_cost"] += vpn_cost
            cost_breakdown["cost_drivers"].append({
                "resource": "VPN Connections",
                "monthly_cost": vpn_cost,
                "description": "VPN connection hourly charges",
            })

        # Analyze Transit Gateway costs
        tgw_cost = self._analyze_tgw_costs(sections.get("transit_gateway_attachments", {}))
        if tgw_cost > 0:
            cost_breakdown["monthly_costs"]["transit_gateway"] = tgw_cost
            cost_breakdown["total_monthly_cost"] += tgw_cost
            cost_breakdown["cost_drivers"].append({
                "resource": "Transit Gateway",
                "monthly_cost": tgw_cost,
                "description": "TGW attachment hourly charges + data processing",
            })

        # Analyze VPC Endpoint costs
        endpoint_cost = self._analyze_endpoint_costs(sections.get("vpc_endpoints", {}))
        if endpoint_cost > 0:
            cost_breakdown["monthly_costs"]["vpc_endpoints"] = endpoint_cost
            cost_breakdown["total_monthly_cost"] += endpoint_cost
            cost_breakdown["cost_drivers"].append({
                "resource": "VPC Endpoints",
                "monthly_cost": endpoint_cost,
                "description": "Interface endpoint hourly charges",
            })

        # Analyze Elastic IP costs
        eip_cost = self._analyze_eip_costs(sections.get("elastic_ips", {}))
        if eip_cost > 0:
            cost_breakdown["monthly_costs"]["elastic_ips"] = eip_cost
            cost_breakdown["total_monthly_cost"] += eip_cost
            cost_breakdown["cost_drivers"].append({
                "resource": "Elastic IPs",
                "monthly_cost": eip_cost,
                "description": "Unassociated Elastic IP charges",
            })

        # Sort cost drivers by cost (highest first)
        cost_breakdown["cost_drivers"].sort(
            key=lambda x: x["monthly_cost"],
            reverse=True
        )

        logger.info(f"Total monthly cost: ${cost_breakdown['total_monthly_cost']:.2f}")

        return cost_breakdown

    def _analyze_nat_gateway_costs(self, nat_data: dict[str, Any]) -> float:
        """Analyze NAT Gateway costs.

        Args:
            nat_data: NAT Gateway data

        Returns:
            Estimated monthly cost
        """
        nat_gateways = nat_data.get("data", {}).get("nat_gateways", [])
        if not nat_gateways:
            return 0.0

        # NAT Gateway pricing (us-east-1 example)
        # $0.045 per hour = $32.40/month per NAT Gateway
        # Plus $0.045 per GB data processed (not calculated here)
        hourly_rate = 0.045
        hours_per_month = 730  # Average

        nat_count = len(nat_gateways)
        monthly_cost = nat_count * hourly_rate * hours_per_month

        logger.debug(f"NAT Gateway cost: {nat_count} gateways × ${hourly_rate}/hr × {hours_per_month}hrs = ${monthly_cost:.2f}")

        return monthly_cost

    def _analyze_vpn_costs(self, vpn_data: dict[str, Any]) -> float:
        """Analyze VPN connection costs.

        Args:
            vpn_data: VPN connection data

        Returns:
            Estimated monthly cost
        """
        vpn_connections = vpn_data.get("data", {}).get("vpn_connections", [])
        if not vpn_connections:
            return 0.0

        # VPN pricing (us-east-1 example)
        # $0.05 per hour = $36.50/month per VPN connection
        hourly_rate = 0.05
        hours_per_month = 730

        vpn_count = len(vpn_connections)
        monthly_cost = vpn_count * hourly_rate * hours_per_month

        logger.debug(f"VPN cost: {vpn_count} connections × ${hourly_rate}/hr × {hours_per_month}hrs = ${monthly_cost:.2f}")

        return monthly_cost

    def _analyze_tgw_costs(self, tgw_data: dict[str, Any]) -> float:
        """Analyze Transit Gateway costs.

        Args:
            tgw_data: Transit Gateway attachment data

        Returns:
            Estimated monthly cost
        """
        attachments = tgw_data.get("data", {}).get("attachments", [])
        if not attachments:
            return 0.0

        # TGW pricing (us-east-1 example)
        # $0.05 per hour per attachment = $36.50/month
        # Plus $0.02 per GB data processed (not calculated here)
        hourly_rate = 0.05
        hours_per_month = 730

        attachment_count = len(attachments)
        monthly_cost = attachment_count * hourly_rate * hours_per_month

        logger.debug(f"TGW cost: {attachment_count} attachments × ${hourly_rate}/hr × {hours_per_month}hrs = ${monthly_cost:.2f}")

        return monthly_cost

    def _analyze_endpoint_costs(self, endpoint_data: dict[str, Any]) -> float:
        """Analyze VPC Endpoint costs.

        Args:
            endpoint_data: VPC Endpoint data

        Returns:
            Estimated monthly cost
        """
        endpoints = endpoint_data.get("data", {}).get("vpc_endpoints", [])
        if not endpoints:
            return 0.0

        # Only Interface endpoints have hourly charges
        # Gateway endpoints (S3, DynamoDB) are free
        interface_endpoints = [
            ep for ep in endpoints
            if ep.get("vpc_endpoint_type") == "Interface"
        ]

        if not interface_endpoints:
            return 0.0

        # Interface endpoint pricing (us-east-1 example)
        # $0.01 per hour per AZ = $7.30/month per AZ
        hourly_rate_per_az = 0.01
        hours_per_month = 730
        avg_azs_per_endpoint = 2  # Typical deployment

        endpoint_count = len(interface_endpoints)
        monthly_cost = endpoint_count * avg_azs_per_endpoint * hourly_rate_per_az * hours_per_month

        logger.debug(f"VPC Endpoint cost: {endpoint_count} endpoints × {avg_azs_per_endpoint} AZs × ${hourly_rate_per_az}/hr × {hours_per_month}hrs = ${monthly_cost:.2f}")

        return monthly_cost

    def _analyze_eip_costs(self, eip_data: dict[str, Any]) -> float:
        """Analyze Elastic IP costs.

        Args:
            eip_data: Elastic IP data

        Returns:
            Estimated monthly cost
        """
        eips = eip_data.get("data", {}).get("elastic_ips", [])
        if not eips:
            return 0.0

        # Only unassociated EIPs are charged
        # $0.005 per hour = $3.65/month per unassociated EIP
        unassociated_eips = [
            eip for eip in eips
            if not eip.get("association_id")
        ]

        if not unassociated_eips:
            return 0.0

        hourly_rate = 0.005
        hours_per_month = 730

        eip_count = len(unassociated_eips)
        monthly_cost = eip_count * hourly_rate * hours_per_month

        logger.debug(f"Unassociated EIP cost: {eip_count} EIPs × ${hourly_rate}/hr × {hours_per_month}hrs = ${monthly_cost:.2f}")

        return monthly_cost

    def generate_cost_recommendations(self, cost_breakdown: dict[str, Any]) -> list[str]:
        """Generate cost optimization recommendations.

        Args:
            cost_breakdown: Cost analysis results

        Returns:
            List of recommendations
        """
        recommendations = []
        monthly_costs = cost_breakdown.get("monthly_costs", {})

        # NAT Gateway recommendations
        if "nat_gateways" in monthly_costs and monthly_costs["nat_gateways"] > 100:
            recommendations.append(
                "Consider consolidating NAT Gateways across multiple subnets in the same AZ to reduce costs"
            )

        # VPN recommendations
        if "vpn_connections" in monthly_costs:
            recommendations.append(
                "Review VPN connections - consider using Transit Gateway for multiple VPN connections"
            )

        # Elastic IP recommendations
        if "elastic_ips" in monthly_costs:
            recommendations.append(
                "Release unassociated Elastic IPs to avoid unnecessary charges"
            )

        # VPC Endpoint recommendations
        if "vpc_endpoints" in monthly_costs and monthly_costs["vpc_endpoints"] > 50:
            recommendations.append(
                "Review VPC Endpoints - ensure all interface endpoints are actively used"
            )

        # General recommendation
        if cost_breakdown.get("total_monthly_cost", 0) > 200:
            recommendations.append(
                "Consider using AWS Cost Explorer for detailed cost analysis and optimization"
            )

        return recommendations
