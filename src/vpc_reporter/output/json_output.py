"""JSON output formatter."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any


def generate_json(data: dict[str, Any]) -> str:
    """Generate JSON output from collected data.

    Args:
        data: Collected VPC data

    Returns:
        JSON formatted string
    """
    # Add metadata
    output = {
        "generated_at": datetime.now().isoformat(),
        "generator": "VPC Reporter v0.1.0",
        **data,
    }

    return json.dumps(output, indent=2, default=str)
