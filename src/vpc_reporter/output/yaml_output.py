"""YAML output formatter."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import yaml


def generate_yaml(data: dict[str, Any]) -> str:
    """Generate YAML output from collected data.

    Args:
        data: Collected VPC data

    Returns:
        YAML formatted string
    """
    # Add metadata
    output = {
        "generated_at": datetime.now().isoformat(),
        "generator": "VPC Reporter v0.1.0",
        **data,
    }

    return yaml.dump(output, default_flow_style=False, sort_keys=False)
