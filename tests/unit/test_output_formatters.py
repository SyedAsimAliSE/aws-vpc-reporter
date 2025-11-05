"""Unit tests for output formatters."""

from __future__ import annotations

import json

import yaml

from vpc_reporter.output.json_output import generate_json
from vpc_reporter.output.yaml_output import generate_yaml


class TestJSONOutput:
    """Test JSON output formatter."""

    def test_generate_json_basic(self) -> None:
        """Test basic JSON generation."""
        data = {
            "vpc_id": "vpc-123",
            "region": "us-east-1",
            "sections": {
                "vpc": {
                    "success": True,
                    "data": {"vpc_id": "vpc-123", "cidr_block": "10.0.0.0/16"},
                }
            },
        }

        result = generate_json(data)

        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed["vpc_id"] == "vpc-123"
        assert parsed["region"] == "us-east-1"

    def test_generate_json_empty(self) -> None:
        """Test JSON generation with empty data."""
        data = {"vpc_id": "vpc-123", "sections": {}}

        result = generate_json(data)

        parsed = json.loads(result)
        assert parsed["vpc_id"] == "vpc-123"
        assert parsed["sections"] == {}

    def test_generate_json_with_none_values(self) -> None:
        """Test JSON generation with None values."""
        data = {
            "vpc_id": "vpc-123",
            "sections": {
                "vpc": {
                    "success": True,
                    "data": {"vpc_id": "vpc-123", "name": None},
                }
            },
        }

        result = generate_json(data)

        parsed = json.loads(result)
        assert parsed["sections"]["vpc"]["data"]["name"] is None


class TestYAMLOutput:
    """Test YAML output formatter."""

    def test_generate_yaml_basic(self) -> None:
        """Test basic YAML generation."""
        data = {
            "vpc_id": "vpc-123",
            "region": "us-east-1",
            "sections": {
                "vpc": {
                    "success": True,
                    "data": {"vpc_id": "vpc-123", "cidr_block": "10.0.0.0/16"},
                }
            },
        }

        result = generate_yaml(data)

        # Should be valid YAML
        parsed = yaml.safe_load(result)
        assert parsed["vpc_id"] == "vpc-123"
        assert parsed["region"] == "us-east-1"

    def test_generate_yaml_empty(self) -> None:
        """Test YAML generation with empty data."""
        data = {"vpc_id": "vpc-123", "sections": {}}

        result = generate_yaml(data)

        parsed = yaml.safe_load(result)
        assert parsed["vpc_id"] == "vpc-123"
        assert parsed["sections"] == {}

    def test_generate_yaml_with_none_values(self) -> None:
        """Test YAML generation with None values."""
        data = {
            "vpc_id": "vpc-123",
            "sections": {
                "vpc": {
                    "success": True,
                    "data": {"vpc_id": "vpc-123", "name": None},
                }
            },
        }

        result = generate_yaml(data)

        parsed = yaml.safe_load(result)
        assert parsed["sections"]["vpc"]["data"]["name"] is None
