"""AWS session management."""

from __future__ import annotations

import aioboto3
import boto3
from botocore.exceptions import NoCredentialsError, ProfileNotFound

from vpc_reporter.aws.exceptions import (
    AWSAuthenticationError,
    AWSProfileNotFoundError,
)


class AWSSession:
    """AWS session manager for both sync and async operations."""

    def __init__(self, profile: str, region: str) -> None:
        """Initialize AWS session.

        Args:
            profile: AWS profile name
            region: AWS region
        """
        self.profile = profile
        self.region = region

        try:
            # Sync session
            self.sync_session = boto3.Session(
                profile_name=profile,
                region_name=region,
            )

            # Async session
            self.async_session = aioboto3.Session(
                profile_name=profile,
                region_name=region,
            )
        except ProfileNotFound as e:
            raise AWSProfileNotFoundError(f"AWS profile '{profile}' not found") from e
        except NoCredentialsError as e:
            raise AWSAuthenticationError("AWS credentials not found") from e

    def get_sync_client(self, service: str) -> any:
        """Get synchronous boto3 client.

        Args:
            service: AWS service name (e.g., 'ec2', 'directconnect')

        Returns:
            Boto3 client
        """
        return self.sync_session.client(service)

    def get_async_client(self, service: str) -> any:
        """Get asynchronous aioboto3 client context manager.

        Args:
            service: AWS service name (e.g., 'ec2', 'directconnect')

        Returns:
            Aioboto3 client context manager
        """
        return self.async_session.client(service, region_name=self.region)
