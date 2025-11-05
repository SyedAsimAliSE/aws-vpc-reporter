"""Custom AWS exceptions."""

from __future__ import annotations


class AWSClientError(Exception):
    """Base exception for AWS client errors."""
    pass


class AWSAuthenticationError(AWSClientError):
    """AWS authentication error."""
    pass


class AWSProfileNotFoundError(AWSClientError):
    """AWS profile not found error."""
    pass


class VPCNotFoundError(AWSClientError):
    """VPC not found error."""
    pass


class ResourceNotFoundError(AWSClientError):
    """AWS resource not found error."""
    pass
