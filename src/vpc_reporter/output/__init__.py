"""Output formatters module."""

from __future__ import annotations


__all__ = [
    "generate_markdown",
    "generate_json",
    "generate_yaml",
    "render_console_output",
]

from vpc_reporter.output.console import render_console_output
from vpc_reporter.output.json_output import generate_json
from vpc_reporter.output.markdown import generate_markdown
from vpc_reporter.output.yaml_output import generate_yaml
