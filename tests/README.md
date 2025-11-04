# Byte Test Suite

This directory contains the comprehensive test suite for the Byte application, which includes both a web app (Litestar) and a Discord bot.

## Directory Structure

```
tests/
├── conftest.py                          # Shared fixtures and test configuration
├── test_pass.py                         # Basic sanity tests
├── server/                              # Web app (Litestar) tests
│   ├── test_guilds.py                  # Guild management tests
│   ├── test_database.py                # Database layer tests
│   └── test_system.py                  # System controller tests
├── bot/                                 # Discord bot tests
│   ├── test_bot_core.py                # Core bot functionality tests
│   ├── test_plugins.py                 # Plugin/command tests
│   └── test_views.py                   # UI component tests
└── integration/                         # Integration tests
    └── test_bot_web_integration.py     # Bot-web API integration tests
```

## Test Categories

### 1. Server Tests (`tests/server/`)

Tests for the Litestar web application:

- **Guild Management** (`test_guilds.py`): Tests for guild CRUD operations, controllers, services, and models
- **Database Layer** (`test_database.py`): Tests for ORM models, relationships, and database operations
- **System Controllers** (`test_system.py`): Tests for health checks and system endpoints

### 2. Bot Tests (`tests/bot/`)

Tests for the Discord bot:

- **Core Bot** (`test_bot_core.py`): Tests for bot initialization, setup, and event handlers
- **Plugins** (`test_plugins.py`): Tests for bot commands and plugins (admin, general, GitHub, config, forums)
- **Views** (`test_views.py`): Tests for Discord UI components (buttons, modals, etc.)

### 3. Integration Tests (`tests/integration/`)

Tests for interaction between the bot and web API:

- **Bot-Web Integration** (`test_bot_web_integration.py`): Tests for bot creating guilds via API, data synchronization

## Running Tests

### Run all tests:

```bash
make test
# or
pytest
```

### Run specific test categories:

```bash
# Run only server tests
pytest tests/server/

# Run only bot tests
pytest tests/bot/

# Run only integration tests
pytest tests/integration/

# Run a specific test file
pytest tests/server/test_guilds.py

# Run a specific test class or function
pytest tests/server/test_guilds.py::TestGuildController::test_create_guild
```

### Run with coverage:

```bash
make coverage
# or
pytest --cov=byte_bot --cov-report=html --cov-report=term
```

### Run with verbose output:

```bash
pytest -v
# or
pytest -vv  # extra verbose
```

## Test Configuration

The test suite is configured via:

- **pyproject.toml**: Contains pytest configuration including async mode and warning filters
- **conftest.py**: Provides shared fixtures for database, HTTP client, Discord mocks, etc.

### Key Fixtures

- `engine`: SQLAlchemy async engine with in-memory SQLite database
- `async_session`: Database session for tests
- `app`: Litestar application instance
- `client`: Async HTTP test client
- `mock_bot`: Mock Discord bot
- `mock_discord_guild`, `mock_discord_member`, `mock_discord_message`: Mock Discord objects
- `sample_guild`, `sample_github_config`, etc.: Sample data fixtures

## Writing New Tests

### 1. Add a new server test:

```python
# tests/server/test_my_feature.py
import pytest
from litestar.testing import AsyncTestClient

class TestMyFeature:
    @pytest.mark.asyncio
    async def test_something(self, client: AsyncTestClient) -> None:
        response = await client.get("/api/my-endpoint")
        assert response.status_code == 200
```

### 2. Add a new bot test:

```python
# tests/bot/test_my_plugin.py
import pytest
from unittest.mock import AsyncMock, MagicMock

class TestMyPlugin:
    @pytest.mark.asyncio
    async def test_command(self, mock_bot: AsyncMock) -> None:
        # Test your bot command
        pass
```

### 3. Add integration test:

```python
# tests/integration/test_my_integration.py
import pytest
from litestar.testing import AsyncTestClient

class TestMyIntegration:
    @pytest.mark.asyncio
    async def test_bot_and_api(self, client: AsyncTestClient, mock_bot: AsyncMock) -> None:
        # Test bot-API interaction
        pass
```

## Test Database

Tests use an in-memory SQLite database that is:

- Created fresh for each test function
- Isolated from the production database
- Automatically cleaned up after tests

## Mocking

The test suite uses mocking extensively for:

- **Discord API**: Mock guilds, members, messages, channels
- **HTTP clients**: Mock external API calls
- **Bot components**: Mock bot instances, cogs, commands

## CI/CD

Tests are run automatically on:

- Every pull request
- Every push to main branch
- Pre-commit hooks (via `make check-all`)

## Troubleshooting

### Tests fail with database errors

Ensure the test database is properly configured in conftest.py. The tests use an in-memory SQLite database by default.

### Tests fail with import errors

Make sure you have all test dependencies installed:

```bash
uv sync --all-extras
# or
pip install -e ".[dev]"
```

### Async tests fail

Ensure pytest-asyncio is installed and configured in pyproject.toml:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

## Coverage Goals

- Overall coverage: > 80%
- Critical paths: > 90%
- New features: 100%

## Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio documentation](https://pytest-asyncio.readthedocs.io/)
- [Litestar testing guide](https://docs.litestar.dev/latest/usage/testing.html)
- [discord.py testing guide](https://discordpy.readthedocs.io/en/stable/ext/test/index.html)
