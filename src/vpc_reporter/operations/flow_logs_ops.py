"""VPC Flow Logs operations."""

from __future__ import annotations

from typing import Any

from loguru import logger

from vpc_reporter.aws.client import AWSClient


class FlowLogsOperations:
    """Operations for VPC Flow Logs resources."""

    def __init__(self, aws_client: AWSClient) -> None:
        """Initialize flow logs operations.

        Args:
            aws_client: AWS client instance
        """
        self.client = aws_client

    def get_flow_logs(self, vpc_id: str) -> dict[str, Any]:
        """Get all flow logs for a VPC.

        Args:
            vpc_id: VPC ID

        Returns:
            Dictionary with flow logs data
        """
        logger.info(f"Getting flow logs for VPC {vpc_id}")

        response = self.client.describe_flow_logs(
            Filters=[{"Name": "resource-id", "Values": [vpc_id]}]
        )

        flow_logs = response.get("FlowLogs", [])

        processed_logs = []
        for log in flow_logs:
            # Parse destination options
            dest_options = log.get("DestinationOptions", {})

            processed_logs.append({
                "flow_log_id": log["FlowLogId"],
                "flow_log_status": log.get("FlowLogStatus"),
                "resource_id": log.get("ResourceId"),
                "traffic_type": log.get("TrafficType"),
                "log_destination_type": log.get("LogDestinationType"),
                "log_destination": log.get("LogDestination"),
                "log_format": log.get("LogFormat"),
                "log_group_name": log.get("LogGroupName"),
                "deliver_logs_status": log.get("DeliverLogsStatus"),
                "deliver_logs_error_message": log.get("DeliverLogsErrorMessage"),
                "deliver_logs_permission_arn": log.get("DeliverLogsPermissionArn"),
                "max_aggregation_interval": log.get("MaxAggregationInterval"),
                "creation_time": log.get("CreationTime"),
                # Destination options
                "file_format": dest_options.get("FileFormat"),
                "hive_compatible_partitions": dest_options.get("HiveCompatiblePartitions", False),
                "per_hour_partition": dest_options.get("PerHourPartition", False),
                "tags": log.get("Tags", []),
                "name": self._get_tag_value(log.get("Tags", []), "Name"),
            })

        logger.info(f"Found {len(processed_logs)} flow logs")

        return {
            "total_count": len(processed_logs),
            "flow_logs": processed_logs,
            "raw_data": flow_logs,
        }

    @staticmethod
    def _get_tag_value(tags: list[dict[str, str]], key: str) -> str | None:
        """Extract tag value by key."""
        for tag in tags:
            if tag.get("Key") == key:
                return tag.get("Value")
        return None
