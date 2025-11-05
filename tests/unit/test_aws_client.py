"""Unit tests for AWS client wrapper."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound

from vpc_reporter.aws.client import AWSClient
from vpc_reporter.aws.exceptions import (
    AWSAuthenticationError,
    AWSClientError,
    AWSProfileNotFoundError,
)


class TestAWSClient:
    """Test AWS client wrapper."""

    def test_init_success(self) -> None:
        """Test successful client initialization."""
        with patch("boto3.Session") as mock_session:
            mock_ec2 = MagicMock()
            mock_dc = MagicMock()
            mock_session.return_value.client.side_effect = [mock_ec2, mock_dc]

            client = AWSClient(profile="test", region="us-east-1")

            assert client.profile == "test"
            assert client.region == "us-east-1"
            assert client.use_cache is True
            assert client.cache_ttl == 300

    def test_init_profile_not_found(self) -> None:
        """Test initialization with non-existent profile."""
        with patch("boto3.Session", side_effect=ProfileNotFound(profile="fake")):
            with pytest.raises(AWSProfileNotFoundError):
                AWSClient(profile="fake", region="us-east-1")

    def test_init_no_credentials(self) -> None:
        """Test initialization with no credentials."""
        with patch("boto3.Session", side_effect=NoCredentialsError()):
            with pytest.raises(AWSAuthenticationError):
                AWSClient(profile="test", region="us-east-1")

    def test_cache_disabled(self) -> None:
        """Test client with caching disabled."""
        with patch("boto3.Session") as mock_session:
            mock_ec2 = MagicMock()
            mock_dc = MagicMock()
            mock_session.return_value.client.side_effect = [mock_ec2, mock_dc]

            client = AWSClient(profile="test", region="us-east-1", use_cache=False)

            assert client.use_cache is False
            assert client.cache is None

    def test_custom_cache_ttl(self) -> None:
        """Test client with custom cache TTL."""
        with patch("boto3.Session") as mock_session:
            mock_ec2 = MagicMock()
            mock_dc = MagicMock()
            mock_session.return_value.client.side_effect = [mock_ec2, mock_dc]

            client = AWSClient(profile="test", region="us-east-1", cache_ttl=600)

            assert client.cache_ttl == 600

    def test_call_with_cache_hit(self) -> None:
        """Test API call with cache hit."""
        with patch("boto3.Session") as mock_session:
            mock_ec2 = MagicMock()
            mock_dc = MagicMock()
            mock_session.return_value.client.side_effect = [mock_ec2, mock_dc]

            client = AWSClient(profile="test", region="us-east-1")

            # Mock cache hit
            if client.cache:
                client.cache.get = MagicMock(return_value={"cached": "data"})

            mock_func = MagicMock()
            result = client._call_with_cache("test_key", mock_func)

            assert result == {"cached": "data"}
            mock_func.assert_not_called()

    def test_call_with_cache_miss(self) -> None:
        """Test API call with cache miss."""
        with patch("boto3.Session") as mock_session:
            mock_ec2 = MagicMock()
            mock_dc = MagicMock()
            mock_session.return_value.client.side_effect = [mock_ec2, mock_dc]

            client = AWSClient(profile="test", region="us-east-1")

            # Mock cache miss
            if client.cache:
                client.cache.get = MagicMock(return_value=None)
                client.cache.set = MagicMock()

            mock_func = MagicMock(return_value={"fresh": "data"})
            result = client._call_with_cache("test_key", mock_func)

            assert result == {"fresh": "data"}
            mock_func.assert_called_once()

    def test_call_with_client_error(self) -> None:
        """Test API call that raises ClientError."""
        with patch("boto3.Session") as mock_session:
            mock_ec2 = MagicMock()
            mock_dc = MagicMock()
            mock_session.return_value.client.side_effect = [mock_ec2, mock_dc]

            client = AWSClient(profile="test", region="us-east-1", use_cache=False)

            error_response = {
                "Error": {"Code": "InvalidVpcID.NotFound", "Message": "VPC not found"}
            }
            mock_func = MagicMock(
                side_effect=ClientError(error_response, "DescribeVpcs")
            )

            with pytest.raises(AWSClientError) as exc_info:
                client._call_with_cache("test_key", mock_func)

            assert "InvalidVpcID.NotFound" in str(exc_info.value)
