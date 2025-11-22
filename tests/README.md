# Byte Bot Test Suite

Comprehensive test infrastructure for the Byte Bot workspace and byte-common package.

## Quick Start

### Run All Tests

```bash
uv run pytest tests/
```

### Run with Coverage

```bash
uv run pytest tests/ --cov=byte_common --cov-report=html
open htmlcov/index.html  # View coverage report
```

### Run Specific Tests

```bash
# Unit tests only
uv run pytest tests/unit/

# Integration tests only
uv run pytest tests/integration/

# Specific test class
uv run pytest tests/unit/test_models.py::TestGuildModel

# Specific test function
uv run pytest tests/unit/test_models.py::TestGuildModel::test_guild_creation -v
```

## Test Organization

```
tests/
├── conftest.py              # Shared fixtures
├── fixtures/
│   └── db_fixtures.py       # Model factory functions
├── integration/
│   └── test_database.py     # Database CRUD and relationship tests
└── unit/
    ├── test_models.py       # SQLAlchemy model tests
    ├── test_schemas.py      # Pydantic schema tests
    └── test_utils.py        # Utility function tests
```

## Test Statistics

- **Total Tests**: 75
- **Coverage**: 70.57%
- **Unit Tests**: 58
- **Integration Tests**: 17

## Available Fixtures

### Database Fixtures (from conftest.py)

- `async_engine` - Async SQLite engine
- `async_session` - Session factory
- `db_session` - Auto-rollback session

### Model Fixtures (from conftest.py)

- `sample_guild` - Pre-configured Guild
- `sample_user` - Pre-configured User
- `sample_github_config` - Pre-configured GitHubConfig
- `sample_forum_config` - Pre-configured ForumConfig

### Factory Functions (from fixtures/db_fixtures.py)

```python
from tests.fixtures.db_fixtures import (
    create_sample_guild,
    create_sample_user,
    create_sample_github_config,
    create_sample_forum_config,
)

# Create with custom values
guild = create_sample_guild(guild_name="Custom Guild", prefix="$")
```

## Writing New Tests

### Unit Test Example

```python
import pytest
from byte_common.models.guild import Guild


class TestMyFeature:
    """Tests for my feature."""

    async def test_something(self, db_session: AsyncSession) -> None:
        """Test description."""
        # Arrange
        guild = Guild(guild_id=123, guild_name="Test")

        # Act
        db_session.add(guild)
        await db_session.flush()

        # Assert
        assert guild.id is not None
```

### Using Fixtures

```python
async def test_with_fixture(
    self,
    db_session: AsyncSession,
    sample_guild: Guild,
) -> None:
    """Test using sample guild fixture."""
    db_session.add(sample_guild)
    await db_session.flush()

    assert sample_guild.guild_name == "Test Guild"
```

## Coverage Goals

| Component   | Current    | Target   |
| ----------- | ---------- | -------- |
| Models      | 100%       | 100%     |
| Schemas     | 100%       | 100%     |
| Utils       | 100%       | 100%     |
| Settings    | 0%         | >80%     |
| Clients     | 0%         | >80%     |
| **Overall** | **70.57%** | **>80%** |

## Test Markers

Configure test markers in pytest:

```bash
# Run only unit tests
uv run pytest -m unit

# Run only integration tests
uv run pytest -m integration
```

## CI/CD Integration

Tests are configured for CI/CD with:

- XML coverage reports (`coverage.xml`)
- HTML coverage reports (`htmlcov/`)
- Pytest exit codes for pass/fail

## Troubleshooting

### Import Errors

If you see `ModuleNotFoundError: No module named 'byte_common'`:

```bash
# Check pytest.ini has correct pythonpath
cat pytest.ini

# Should contain:
# pythonpath = packages/byte-common/src
```

### Async Test Issues

If async tests fail to run:

```bash
# Check pytest.ini has asyncio mode
# asyncio_mode = auto

# Ensure pytest-asyncio is installed
uv sync
```

### Database Errors

If database tests fail:

```bash
# Ensure aiosqlite is installed
uv add --dev aiosqlite

# Check foreign key constraints are enabled in conftest.py
```

## Performance

Current test execution time: ~0.4-0.6 seconds for all 75 tests

- Unit tests: ~0.1s
- Integration tests: ~0.3s (includes database setup/teardown)

## Documentation

For detailed setup and configuration, see:

- `TEST_INFRASTRUCTURE_REPORT.md` - Complete setup documentation
- `pyproject.toml` - pytest and coverage configuration
- `.coveragerc` - Coverage settings
- `pytest.ini` - Pytest configuration

## Contributing

When adding new code to byte-common:

1. Write tests first (TDD)
2. Ensure >80% coverage for new modules
3. Run full test suite before committing
4. Update fixtures if adding new models
