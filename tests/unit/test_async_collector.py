"""Unit tests for Async Collector."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from vpc_reporter.aws.client import AWSClient
from vpc_reporter.operations.async_collector import (
    _collect_section_async,
    _run_in_executor,
    collect_all_data_async,
)


@pytest.fixture
def mock_aws_client() -> AWSClient:
    """Create a mock AWS client."""
    client = MagicMock(spec=AWSClient)
    client.region = "us-east-1"
    client.profile = "test"
    return client


class TestAsyncCollector:
    """Test async collector functions."""

    @pytest.mark.asyncio
    async def test_run_in_executor(self) -> None:
        """Test running function in executor."""
        def sync_func(x: int, y: int) -> int:
            return x + y

        result = await _run_in_executor(sync_func, 2, 3)
        assert result == 5

    @pytest.mark.asyncio
    async def test_collect_section_async_success(self) -> None:
        """Test successful section collection."""
        mock_collector = MagicMock(return_value={"vpc_id": "vpc-123"})

        result = await _collect_section_async("vpc", mock_collector)

        assert result["success"] is True
        assert result["data"]["vpc_id"] == "vpc-123"

    @pytest.mark.asyncio
    async def test_collect_section_async_error(self) -> None:
        """Test section collection with error."""
        mock_collector = MagicMock(side_effect=Exception("Test error"))

        result = await _collect_section_async("vpc", mock_collector)

        assert result["success"] is False
        assert "Test error" in result["error"]

    @pytest.mark.asyncio
    async def test_collect_all_data_async(self, mock_aws_client: AWSClient) -> None:
        """Test collecting all data asynchronously."""
        # Mock all operations
        with patch('vpc_reporter.operations.async_collector.VPCOperations') as mock_vpc_ops:
            mock_vpc_instance = MagicMock()
            mock_vpc_instance.get_vpc_details.return_value = {
                "vpc_id": "vpc-123",
                "cidr_block": "10.0.0.0/16",
                "dhcp_options_id": "dopt-123",
            }
            mock_vpc_ops.return_value = mock_vpc_instance

            with patch('vpc_reporter.operations.async_collector.SubnetOperations') as mock_subnet_ops:
                mock_subnet_instance = MagicMock()
                mock_subnet_instance.get_subnets.return_value = {
                    "total_count": 1,
                    "subnets": [{"subnet_id": "subnet-123"}],
                }
                mock_subnet_ops.return_value = mock_subnet_instance

                # Mock all other operations to return empty data
                with patch('vpc_reporter.operations.async_collector.RouteTableOperations'):
                    with patch('vpc_reporter.operations.async_collector.SecurityGroupOperations'):
                        with patch('vpc_reporter.operations.async_collector.NetworkACLOperations'):
                            with patch('vpc_reporter.operations.async_collector.InternetGatewayOperations'):
                                with patch('vpc_reporter.operations.async_collector.NATGatewayOperations'):
                                    with patch('vpc_reporter.operations.async_collector.ElasticIPOperations'):
                                        with patch('vpc_reporter.operations.async_collector.VPCEndpointOperations'):
                                            with patch('vpc_reporter.operations.async_collector.VPCPeeringOperations'):
                                                with patch('vpc_reporter.operations.async_collector.TransitGatewayAttachmentOperations'):
                                                    with patch('vpc_reporter.operations.async_collector.CustomerGatewayOperations'):
                                                        with patch('vpc_reporter.operations.async_collector.VirtualPrivateGatewayOperations'):
                                                            with patch('vpc_reporter.operations.async_collector.DHCPOptionsOperations'):
                                                                with patch('vpc_reporter.operations.async_collector.FlowLogsOperations'):
                                                                    with patch('vpc_reporter.operations.async_collector.VPNConnectionOperations'):
                                                                        with patch('vpc_reporter.operations.async_collector.NetworkInterfaceOperations'):
                                                                            with patch('vpc_reporter.operations.async_collector.VPCAttributesOperations'):
                                                                                with patch('vpc_reporter.operations.async_collector.DirectConnectVIFOperations'):
                                                                                    result = await collect_all_data_async(
                                                                                        mock_aws_client,
                                                                                        "vpc-123",
                                                                                        sections=["vpc", "subnets"],
                                                                                    )

        assert result["vpc_id"] == "vpc-123"
        assert result["region"] == "us-east-1"
        assert result["profile"] == "test"
        assert "vpc" in result["sections"]
        assert "subnets" in result["sections"]

    @pytest.mark.asyncio
    async def test_collect_section_async_handles_exception(self) -> None:
        """Test that section collection handles exceptions gracefully."""
        def failing_collector() -> None:
            raise ValueError("Test error")

        result = await _collect_section_async("test_section", failing_collector)

        assert result["success"] is False
        assert "Test error" in result["error"]
