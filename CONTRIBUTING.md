# Contributing to VPC Reporter

Thank you for your interest in contributing to VPC Reporter! This document provides guidelines and information for contributors.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- [UV](https://docs.astral.sh/uv/) package manager
- AWS account (for testing)
- Git

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/vpc-reporter.git
   cd vpc-reporter
   ```

2. **Install dependencies**
   ```bash
   uv sync
   uv sync --extra dev
   ```

3. **Run tests to verify setup**
   ```bash
   uv run pytest tests/ -v
   ```

## Development Workflow

### Making Changes

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the project's coding standards.

3. Run tests and ensure they pass:
   ```bash
   uv run pytest tests/ -v
   uv run ruff check src/
   uv run mypy src/
   ```

4. Commit your changes with a descriptive message:
   ```bash
   git commit -m "feat: add new VPC section for XYZ"
   ```

5. Push to your fork and create a pull request.

### Code Style

This project uses several tools to maintain code quality:

- **Black**: Code formatting
- **Ruff**: Linting and import sorting
- **MyPy**: Type checking

Run all quality checks:
```bash
uv run black src/
uv run ruff check src/
uv run mypy src/
```

### Testing

#### Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov --cov-report=term

# Run specific test categories
uv run pytest tests/unit/ -v
uv run pytest tests/integration/ -v
```

#### Writing Tests

- Unit tests go in `tests/unit/`
- Integration tests go in `tests/integration/`
- End-to-end tests go in `tests/e2e/`
- AWS-dependent tests should use the `@pytest.mark.aws` marker

#### Test Structure

```python
import pytest
from unittest.mock import Mock, patch

@pytest.mark.unit
def test_your_function():
    # Arrange
    # Act
    # Assert
    pass
```

## Project Structure

```
vpc-reporter/
├── src/vpc_reporter/
│   ├── operations/          # VPC section operations
│   ├── output/              # Output formatters
│   ├── cost/                # Cost analysis
│   ├── diagrams/            # Diagram generation
│   ├── config/              # Configuration management
│   ├── cache/               # Caching layer
│   ├── aws/                 # AWS client wrappers
│   └── cli/                 # CLI interface
├── tests/                   # Test suite
├── docs/                    # Documentation
├── scripts/                 # Utility scripts
└── pyproject.toml          # Project configuration
```

## Adding New VPC Sections

To add a new VPC section:

1. **Create operation class** in `src/vpc_reporter/operations/`
2. **Implement collector methods** for synchronous and async modes
3. **Add output formatters** in `src/vpc_reporter/output/`
4. **Write tests** in `tests/integration/`
5. **Update documentation** in README.md

Example operation structure:
```python
from vpc_reporter.operations.base import BaseOperation

class NewSectionOperation(BaseOperation):
    async def collect(self) -> dict:
        # Collect AWS data
        pass
    
    def format_console(self, data: dict) -> str:
        # Format for console output
        pass
    
    def format_markdown(self, data: dict) -> str:
        # Format for markdown output
        pass
```

## Submitting Pull Requests

### PR Requirements

- All tests must pass
- Code must pass linting and type checking
- Include tests for new functionality
- Update documentation as needed
- Use conventional commit messages

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All tests pass
- [ ] New tests added for new functionality
- [ ] Manual testing performed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
```

## Release Process

Releases are handled by maintainers using semantic versioning:

- `MAJOR.MINOR.PATCH`
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)

## Getting Help

- Check existing [Issues](https://github.com/valour/vpc-reporter/issues)
- Create a new issue for bugs or feature requests
- Join discussions in existing issues

## Code of Conduct

Please be respectful and professional in all interactions. We follow the [Python Community Code of Conduct](https://www.python.org/psf/conduct/).

Thank you for contributing! 🚀
