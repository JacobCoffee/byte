# Byte API Service

> **Version**: 0.2.0 **Python**: 3.13+ **Framework**: Litestar 2.4.3+

## Overview

The **Byte API Service** is the REST API microservice for Byte Bot, providing HTTP endpoints for guild management,
GitHub integration, and system operations. This service replaces the monolithic web service and operates independently
of the Discord bot.

## Purpose

- **REST API Endpoints**: Guild CRUD, GitHub config, forum settings
- **Database Operations**: Primary data store interface via Advanced Alchemy ORM
- **OpenAPI Documentation**: Swagger/ReDoc UI for API exploration
- **Health Monitoring**: System health checks and status endpoints
- **Web Dashboard**: Server-side rendered dashboard (Jinja2 templates)

## Architecture

The API service is built on:

- **Litestar**: High-performance ASGI framework
- **Advanced Alchemy**: Repository pattern over SQLAlchemy 2.0
- **PostgreSQL**: Primary database (async via asyncpg)
- **Pydantic**: Request/response validation and settings management

## Dependencies

### Core Dependencies

- `byte-common`: Shared models, utilities, and database schemas
- `litestar[full]>=2.4.3`: Web framework with full plugin support
- `advanced-alchemy>=0.6.1`: ORM and repository pattern
- `asyncpg>=0.29.0`: Async PostgreSQL driver
- `alembic>=1.13.0`: Database migrations

### Integration Dependencies

- `githubkit[auth-app]`: GitHub API client
- `httpx`: Async HTTP client
- `pydantic>=2.5.2`: Data validation
- `pydantic-settings>=2.1.0`: Configuration management
- `PyJWT>=2.8.0`: JWT token handling

## Installation

```bash
# From repository root
cd services/api

# Install dependencies with uv
uv sync

# Or install as editable package
uv pip install -e .
```

## Configuration

Set the following environment variables (or use `.env` file):

```bash
# Database
DB_URL=postgresql+asyncpg://user:pass@localhost:5432/byte
DB_POOL_DISABLE=True  # Use NullPool in production

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
ENVIRONMENT=dev  # dev, test, or prod
SECRET_KEY=your-secret-key

# GitHub Integration
GITHUB_APP_ID=your-app-id
GITHUB_APP_PRIVATE_KEY=your-private-key
GITHUB_APP_CLIENT_ID=your-client-id
GITHUB_APP_CLIENT_SECRET=your-client-secret

# Logging
LOG_LEVEL=INFO
DEBUG=False
```

## Running the Service

```bash
# Development mode with auto-reload
uv run python -m byte_api --reload --debug

# Production mode
uv run python -m byte_api --http-workers 4

# With custom host/port
uv run python -m byte_api --host 0.0.0.0 --port 8080
```

## Development

### Database Migrations

```bash
# Apply migrations
uv run alembic upgrade head

# Create new migration
uv run alembic revision --autogenerate -m "description"

# Rollback
uv run alembic downgrade -1
```

### Testing

```bash
# Run tests
uv run pytest

# With coverage
uv run pytest --cov=byte_api --cov-report=html
```

### Code Quality

```bash
# Linting
uv run ruff check .

# Formatting
uv run ruff format .

# Type checking
uv run ty check byte_api
```

## API Endpoints

### Guild Management

- `GET /api/guilds` - List all guilds (paginated)
- `POST /api/guilds` - Create guild
- `GET /api/guilds/{guild_id}` - Get guild details
- `PATCH /api/guilds/{guild_id}` - Update guild
- `DELETE /api/guilds/{guild_id}` - Delete guild

### Configuration

- `GET /api/guilds/{guild_id}/github` - GitHub config
- `GET /api/guilds/{guild_id}/sotags` - Stack Overflow tags
- `GET /api/guilds/{guild_id}/allowed-users` - Allowed users
- `GET /api/guilds/{guild_id}/forum` - Forum config

### System

- `GET /health` - Health check
- `GET /api/system/info` - System information

### Documentation

- `GET /api/swagger` - Swagger UI
- `GET /api/redoc` - ReDoc UI
- `GET /api/schema/openapi.json` - OpenAPI schema

## Project Structure

```
services/api/
├── src/
│   └── byte_api/
│       ├── __init__.py
│       ├── __main__.py          # Entry point
│       ├── app.py               # Litestar app factory
│       ├── lib/                 # Infrastructure
│       │   ├── settings.py
│       │   ├── cors.py
│       │   ├── openapi.py
│       │   ├── db/
│       │   └── log/
│       └── domain/              # Business logic
│           ├── guilds/
│           ├── github/
│           ├── system/
│           └── web/
├── tests/
├── pyproject.toml
└── README.md
```

## Migration Notes

This service is part of Phase 1 (API Layer Extraction) of the microservices migration. It consolidates functionality
from:

- `byte_api/app.py` - Litestar app factory
- `byte_api/domain/` - Business domains
- `byte_api/lib/` - Infrastructure code (database, settings, etc.)

The Discord bot will communicate with this service via HTTP rather than direct database access.

## Deployment

### Docker

```bash
# Build image
docker build -t byte-api:latest .

# Run container
docker run -p 8000:8000 --env-file .env byte-api:latest
```

### Railway

Deploy as a standalone service with PostgreSQL database plugin attached.

## Troubleshooting

### Database Connection Issues

- Verify `DB_URL` format: `postgresql+asyncpg://user:pass@host:port/db`
- Ensure PostgreSQL is running and accessible
- Check firewall/network settings

### Migration Errors

- Ensure database is up to date: `uv run alembic upgrade head`
- Check migration scripts in `byte_common` package
- Verify no other processes are holding locks

### Import Errors

- Install dependencies: `uv sync`
- Verify `byte-common` is installed in same environment
- Check Python version: `python --version` (should be 3.13+)

## Additional Resources

- [Litestar Documentation](https://docs.litestar.dev/)
- [Advanced Alchemy Documentation](https://docs.advanced-alchemy.litestar.dev/)
- [Main Repository](https://github.com/JacobCoffee/byte)
- [Migration Plan](../../PLAN.md)

## License

MIT License - See LICENSE file in repository root.

## Maintainer

Jacob Coffee (@JacobCoffee) - jacob@z7x.org
