"""AWS client wrapper with error handling and caching."""

from __future__ import annotations

from typing import Any

import boto3
from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound
from loguru import logger

from vpc_reporter.aws.exceptions import (
    AWSAuthenticationError,
    AWSClientError,
    AWSProfileNotFoundError,
)
from vpc_reporter.cache.cache import CacheManager


class AWSClient:
    """AWS client wrapper with error handling and optional caching."""

    def __init__(
        self,
        profile: str,
        region: str,
        use_cache: bool = True,
        cache_ttl: int = 300,
    ) -> None:
        """Initialize AWS client.

        Args:
            profile: AWS profile name
            region: AWS region
            use_cache: Enable caching of API responses
            cache_ttl: Cache time-to-live in seconds
        """
        self.profile = profile
        self.region = region
        self.use_cache = use_cache
        self.cache_ttl = cache_ttl

        # Initialize cache if enabled
        self.cache = CacheManager() if use_cache else None

        # Initialize session and clients
        try:
            self.session = boto3.Session(
                profile_name=profile,
                region_name=region,
            )
            self.ec2 = self.session.client("ec2")
            self.directconnect = self.session.client("directconnect")

            logger.info(
                f"Initialized AWS client for profile={profile}, region={region}"
            )
        except ProfileNotFound as e:
            raise AWSProfileNotFoundError(f"AWS profile '{profile}' not found") from e
        except NoCredentialsError as e:
            raise AWSAuthenticationError("AWS credentials not found") from e
        except Exception as e:
            raise AWSClientError(f"Failed to initialize AWS client: {e}") from e

    def _call_with_cache(
        self,
        cache_key: str,
        func: Any,
        *args: Any,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Call AWS API with optional caching.

        Args:
            cache_key: Unique cache key
            func: AWS API function to call
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            API response
        """
        # Check cache if enabled
        if self.cache:
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result  # type: ignore[no-any-return]

        # Call API
        try:
            result = func(*args, **kwargs)

            # Store in cache if enabled
            if self.cache:
                self.cache.set(cache_key, result, ttl=self.cache_ttl)
                logger.debug(f"Cached result for {cache_key}")

            return result  # type: ignore[no-any-return]
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_message = e.response.get("Error", {}).get("Message", str(e))
            raise AWSClientError(
                f"AWS API error ({error_code}): {error_message}"
            ) from e
        except Exception as e:
            raise AWSClientError(f"Unexpected error calling AWS API: {e}") from e

    # VPC Operations
    def describe_vpcs(self, **kwargs: Any) -> dict[str, Any]:
        """Describe VPCs."""
        cache_key = f"describe_vpcs:{self.region}:{kwargs}"
        return self._call_with_cache(cache_key, self.ec2.describe_vpcs, **kwargs)

    def describe_subnets(self, **kwargs: Any) -> dict[str, Any]:
        """Describe subnets."""
        cache_key = f"describe_subnets:{self.region}:{kwargs}"
        return self._call_with_cache(cache_key, self.ec2.describe_subnets, **kwargs)

    def describe_route_tables(self, **kwargs: Any) -> dict[str, Any]:
        """Describe route tables."""
        cache_key = f"describe_route_tables:{self.region}:{kwargs}"
        return self._call_with_cache(
            cache_key, self.ec2.describe_route_tables, **kwargs
        )

    def describe_internet_gateways(self, **kwargs: Any) -> dict[str, Any]:
        """Describe internet gateways."""
        cache_key = f"describe_internet_gateways:{self.region}:{kwargs}"
        return self._call_with_cache(
            cache_key, self.ec2.describe_internet_gateways, **kwargs
        )

    def describe_nat_gateways(self, **kwargs: Any) -> dict[str, Any]:
        """Describe NAT gateways."""
        cache_key = f"describe_nat_gateways:{self.region}:{kwargs}"
        return self._call_with_cache(
            cache_key, self.ec2.describe_nat_gateways, **kwargs
        )

    def describe_addresses(self, **kwargs: Any) -> dict[str, Any]:
        """Describe Elastic IP addresses."""
        cache_key = f"describe_addresses:{self.region}:{kwargs}"
        return self._call_with_cache(cache_key, self.ec2.describe_addresses, **kwargs)

    def describe_vpc_peering_connections(self, **kwargs: Any) -> dict[str, Any]:
        """Describe VPC peering connections."""
        cache_key = f"describe_vpc_peering_connections:{self.region}:{kwargs}"
        return self._call_with_cache(
            cache_key, self.ec2.describe_vpc_peering_connections, **kwargs
        )

    def describe_transit_gateway_vpc_attachments(self, **kwargs: Any) -> dict[str, Any]:
        """Describe Transit Gateway VPC attachments."""
        cache_key = f"describe_transit_gateway_vpc_attachments:{self.region}:{kwargs}"
        return self._call_with_cache(
            cache_key, self.ec2.describe_transit_gateway_vpc_attachments, **kwargs
        )

    def describe_vpn_connections(self, **kwargs: Any) -> dict[str, Any]:
        """Describe VPN connections."""
        cache_key = f"describe_vpn_connections:{self.region}:{kwargs}"
        return self._call_with_cache(
            cache_key, self.ec2.describe_vpn_connections, **kwargs
        )

    def describe_vpn_gateways(self, **kwargs: Any) -> dict[str, Any]:
        """Describe VPN gateways."""
        cache_key = f"describe_vpn_gateways:{self.region}:{kwargs}"
        return self._call_with_cache(
            cache_key, self.ec2.describe_vpn_gateways, **kwargs
        )

    def describe_customer_gateways(self, **kwargs: Any) -> dict[str, Any]:
        """Describe customer gateways."""
        cache_key = f"describe_customer_gateways:{self.region}:{kwargs}"
        return self._call_with_cache(
            cache_key, self.ec2.describe_customer_gateways, **kwargs
        )

    def describe_vpc_endpoints(self, **kwargs: Any) -> dict[str, Any]:
        """Describe VPC endpoints."""
        cache_key = f"describe_vpc_endpoints:{self.region}:{kwargs}"
        return self._call_with_cache(
            cache_key, self.ec2.describe_vpc_endpoints, **kwargs
        )

    def describe_security_groups(self, **kwargs: Any) -> dict[str, Any]:
        """Describe security groups."""
        cache_key = f"describe_security_groups:{self.region}:{kwargs}"
        return self._call_with_cache(
            cache_key, self.ec2.describe_security_groups, **kwargs
        )

    def describe_network_acls(self, **kwargs: Any) -> dict[str, Any]:
        """Describe network ACLs."""
        cache_key = f"describe_network_acls:{self.region}:{kwargs}"
        return self._call_with_cache(
            cache_key, self.ec2.describe_network_acls, **kwargs
        )

    def describe_network_interfaces(self, **kwargs: Any) -> dict[str, Any]:
        """Describe network interfaces."""
        cache_key = f"describe_network_interfaces:{self.region}:{kwargs}"
        return self._call_with_cache(
            cache_key, self.ec2.describe_network_interfaces, **kwargs
        )

    def describe_dhcp_options(self, **kwargs: Any) -> dict[str, Any]:
        """Describe DHCP options."""
        cache_key = f"describe_dhcp_options:{self.region}:{kwargs}"
        return self._call_with_cache(
            cache_key, self.ec2.describe_dhcp_options, **kwargs
        )

    def describe_flow_logs(self, **kwargs: Any) -> dict[str, Any]:
        """Describe VPC flow logs."""
        cache_key = f"describe_flow_logs:{self.region}:{kwargs}"
        return self._call_with_cache(cache_key, self.ec2.describe_flow_logs, **kwargs)

    def describe_virtual_interfaces(self, **kwargs: Any) -> dict[str, Any]:
        """Describe Direct Connect virtual interfaces."""
        cache_key = f"describe_virtual_interfaces:{self.region}:{kwargs}"
        return self._call_with_cache(
            cache_key, self.directconnect.describe_virtual_interfaces, **kwargs
        )

    def describe_vpc_attribute(self, **kwargs: Any) -> dict[str, Any]:
        """Describe VPC attribute (requires VpcId and Attribute parameters)."""
        cache_key = f"describe_vpc_attribute:{self.region}:{kwargs}"
        return self._call_with_cache(
            cache_key, self.ec2.describe_vpc_attribute, **kwargs
        )
