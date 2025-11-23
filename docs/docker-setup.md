# Docker Compose Setup Guide

This guide covers local development and production deployment using Docker Compose for the Byte Bot microservices
architecture.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Development Workflow](#development-workflow)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)
- [Testing](#testing)

---

## Prerequisites

### Required Software

- **Docker**: Version 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose**: Version 2.0+ (bundled with Docker Desktop)
- **Git**: For cloning the repository
- **Discord Bot Token**: From [Discord Developer Portal](https://discord.com/developers/applications)

### Optional but Recommended

- **make**: For using Makefile commands (pre-installed on macOS/Linux)
- **uv**: For local Python development without Docker

### System Requirements

- **RAM**: Minimum 4GB, recommended 8GB
- **Disk Space**: ~2GB for Docker images and volumes
- **Network**: Internet connection for pulling Docker images

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/JacobCoffee/byte.git
cd byte
```

### 2. Configure Environment

```bash
# Copy the Docker environment template
cp .env.docker.example .env

# Edit .env with your credentials
# Required: DISCORD_TOKEN, SECRET_KEY, GITHUB_APP_* credentials
nano .env  # or use your preferred editor
```

**Minimum required variables:**

```env
DISCORD_TOKEN=your_discord_bot_token_here
SECRET_KEY=generate_a_secure_secret_key
```

### 3. Start All Services

```bash
# Using make (recommended)
make docker-up

# Or using docker-compose directly
docker-compose up -d
```

### 4. View Logs

```bash
# All services
make docker-logs

# Specific service
make docker-logs-api
make docker-logs-bot
make docker-logs-postgres
```

### 5. Access the Application

- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/swagger
- **Health Check**: http://localhost:8000/health
- **PostgreSQL**: localhost:5432 (credentials in .env)

---

## Configuration

### Environment Files

#### Development: `.env`

Copy from `.env.docker.example` and configure:

```env
# Discord credentials
DISCORD_TOKEN=your_token_here
DISCORD_DEV_GUILD_ID=your_guild_id  # Optional, for slash command sync
DISCORD_DEV_USER_ID=your_user_id    # Optional, for admin commands

# Database (uses docker service name)
DB_URL=postgresql+asyncpg://byte:bot@postgres:5432/byte

# API service endpoint (for bot)
API_SERVICE_URL=http://api:8000

# Application settings
ENVIRONMENT=dev
DEBUG=True
LOG_LEVEL=10  # DEBUG level

# Security
SECRET_KEY=generate_a_secure_key_min_32_chars

# GitHub integration (optional, for issue creation)
GITHUB_APP_ID=your_app_id
GITHUB_APP_PRIVATE_KEY=your_private_key_pem_format
```

#### Production: `.env` + `docker-compose.prod.yml`

See [Production Deployment](#production-deployment) section.

### Service Configuration

Each service can be configured via environment variables:

| Service    | Port | Environment Variables                               |
| ---------- | ---- | --------------------------------------------------- |
| PostgreSQL | 5432 | `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` |
| API        | 8000 | `SERVER_HOST`, `SERVER_PORT`, `SERVER_HTTP_WORKERS` |
| Bot        | -    | `DISCORD_TOKEN`, `API_SERVICE_URL`                  |

---

## Development Workflow

### Starting Development Environment

```bash
# Start all services with logs
make docker-up

# Or in background
docker-compose up -d
```

**What happens:**

1. PostgreSQL starts and runs health checks
2. API service waits for PostgreSQL to be healthy
3. API runs database migrations (`alembic upgrade head`)
4. API starts with hot-reload enabled
5. Bot service waits for API to be healthy
6. Bot connects to Discord

### Making Code Changes

**Hot Reload** is enabled in development mode:

- **API**: Changes to `services/api/src/**/*.py` trigger automatic reload
- **Bot**: Changes to `services/bot/src/**/*.py` require manual restart
- **Shared Package**: Changes to `packages/byte-common/` require restart

```bash
# Restart a specific service
make docker-restart-api
make docker-restart-bot

# Rebuild after dependency changes
make docker-rebuild
```

### Running Database Migrations

```bash
# Create a new migration
make migrations MIGRATION_MESSAGE="add user preferences"

# This runs:
# docker-compose exec api uv run alembic revision --autogenerate -m "add user preferences"

# Apply migrations
docker-compose exec api alembic upgrade head

# Rollback one migration
docker-compose exec api alembic downgrade -1
```

### Accessing Service Shells

```bash
# API service bash
make docker-shell-api

# Bot service bash
make docker-shell-bot

# PostgreSQL shell
make docker-shell-postgres
```

### Viewing Logs

```bash
# Follow all logs
make docker-logs

# Follow specific service
docker-compose logs -f api
docker-compose logs -f bot

# View last 100 lines
docker-compose logs --tail=100 api
```

### Running Tests

```bash
# Run tests inside API container
docker-compose exec api uv run pytest

# With coverage
docker-compose exec api uv run pytest --cov=byte_api

# Run tests locally (requires uv)
make test
make coverage
```

### Stopping Services

```bash
# Stop but keep volumes (data persists)
make docker-down

# Stop and remove volumes (clean slate)
make docker-down-volumes
```

---

## Production Deployment

### Using docker-compose.prod.yml

Production deployment uses layered compose files:

```bash
# Start with production overrides
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Or set via environment
export COMPOSE_FILE=docker-compose.yml:docker-compose.prod.yml
docker-compose up -d
```

### Production Configuration

**Key differences from development:**

1. **No Hot Reload**: Volume mounts removed
2. **Multiple Workers**: API runs with 4 workers (configurable)
3. **Resource Limits**: CPU and memory constraints
4. **Restart Policies**: Automatic restart on failure
5. **Logging**: Larger log files (50MB max)
6. **Security**: No exposed PostgreSQL port

**Production `.env` example:**

```env
# Discord
DISCORD_TOKEN=prod_token_from_secrets_manager

# Database
DB_URL=postgresql+asyncpg://byte:strong_password@postgres:5432/byte

# API
API_SERVICE_URL=http://api:8000
SERVER_HTTP_WORKERS=4

# Application
ENVIRONMENT=prod
DEBUG=False
LOG_LEVEL=20  # INFO level

# Security
SECRET_KEY=use_strong_secret_from_secrets_manager

# GitHub
GITHUB_APP_ID=prod_app_id
GITHUB_APP_PRIVATE_KEY=prod_private_key
```

### Railway Deployment

Railway supports Docker Compose directly:

1. **Create Railway Project**: Connect GitHub repository
2. **Configure Services**:
   - PostgreSQL: Use Railway PostgreSQL service
   - API: Deploy from `services/api/Dockerfile`
   - Bot: Deploy from `services/bot/Dockerfile`
3. **Set Environment Variables**: In Railway dashboard
4. **Deploy**: Railway auto-deploys on git push

**Alternative: Use individual Dockerfiles**

See `services/*/railway.json` for single-service configurations.

---

## Troubleshooting

### Common Issues

#### 1. "Service 'api' failed to build"

**Cause**: Missing dependencies or lockfile issues.

**Solution**:

```bash
# Rebuild without cache
docker-compose build --no-cache api

# Update lockfile locally
uv lock --upgrade
git add uv.lock && git commit -m "chore: update uv.lock"
```

#### 2. "Database connection refused"

**Cause**: PostgreSQL not ready or healthcheck failing.

**Solution**:

```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Verify health
docker-compose ps

# Restart PostgreSQL
docker-compose restart postgres
```

#### 3. "Bot: Improper token has been passed"

**Cause**: Invalid `DISCORD_TOKEN` in `.env`.

**Solution**:

```bash
# Verify token format (should start with a long string)
cat .env | grep DISCORD_TOKEN

# Get new token from Discord Developer Portal
# Update .env and restart
docker-compose restart bot
```

#### 4. "Port 5432 already in use"

**Cause**: Local PostgreSQL running on same port.

**Solution**:

```bash
# Option 1: Stop local PostgreSQL
sudo systemctl stop postgresql  # Linux
brew services stop postgresql   # macOS

# Option 2: Change port in docker-compose.yml
ports:
  - "5433:5432"  # Map to different host port
```

#### 5. "API returns 503 Service Unavailable"

**Cause**: Database migrations not applied or database not ready.

**Solution**:

```bash
# Check API logs
docker-compose logs api

# Run migrations manually
docker-compose exec api alembic upgrade head

# Restart API
docker-compose restart api
```

### Debug Mode

Enable verbose logging:

```bash
# Set in .env
LOG_LEVEL=10
DEBUG=True

# Restart services
docker-compose restart
```

### Clean Slate

Start fresh with no data:

```bash
# Stop all services and remove volumes
docker-compose down -v

# Remove images (optional)
docker-compose down --rmi all

# Start fresh
docker-compose up -d --build
```

---

## Testing

### Local Testing Checklist

Before deploying to production, test locally:

#### 1. Build Test

```bash
make docker-rebuild
# ✅ All services build successfully
# ✅ No build errors or warnings
```

#### 2. Health Checks

```bash
# Wait 60 seconds for services to start
sleep 60

# Check health endpoints
curl http://localhost:8000/health
# Expected: {"status":"ok","database":"healthy"}

curl http://localhost:8000/health/ready
# Expected: {"status":"ready"}

curl http://localhost:8000/health/live
# Expected: {"status":"alive"}

# ✅ All health checks return 200 OK
```

#### 3. Database Connectivity

```bash
# Access PostgreSQL
make docker-shell-postgres

# Run query
SELECT COUNT(*) FROM guilds;

# ✅ Database is accessible and migrations applied
```

#### 4. API Endpoints

```bash
# OpenAPI docs
curl http://localhost:8000/api/swagger
# ✅ Returns Swagger UI HTML

# System health (comprehensive)
curl http://localhost:8000/system/health
# ✅ Returns system status with database + bot status
```

#### 5. Bot Connectivity

```bash
# Check bot logs
docker-compose logs bot | grep "Logged in as"

# ✅ Bot successfully connects to Discord
# ✅ No authentication errors
```

#### 6. Inter-Service Communication

```bash
# Bot should call API service
docker-compose logs bot | grep "http://api:8000"

# ✅ Bot successfully communicates with API
# ✅ No connection refused errors
```

#### 7. Hot Reload (Development)

```bash
# Make a change to services/api/src/byte_api/app.py
# (add a comment)

# Watch logs
docker-compose logs -f api

# ✅ API auto-reloads within 2-3 seconds
```

#### 8. Restart Resilience

```bash
# Stop and start services
docker-compose restart

# Wait 30 seconds
sleep 30

# Check health
curl http://localhost:8000/health

# ✅ All services restart successfully
# ✅ Health checks pass after restart
```

#### 9. Volume Persistence

```bash
# Create test data (via API or bot)
# Stop services
docker-compose down

# Start again (without -v flag)
docker-compose up -d

# ✅ Data persists across restarts
```

#### 10. Production Build Test

```bash
# Test production configuration
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# ✅ Builds with production settings
# ✅ No volume mounts
# ✅ Multiple workers for API
```

### Automated Testing

Create a test script:

```bash
#!/bin/bash
# test-docker.sh

set -e

echo "🧪 Testing Docker Compose setup..."

# Start services
docker-compose up -d
sleep 60

# Test health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    exit 1
fi

# Test API
if curl -f http://localhost:8000/api/schema/openapi.json > /dev/null 2>&1; then
    echo "✅ API accessible"
else
    echo "❌ API not accessible"
    exit 1
fi

# Check bot
if docker-compose logs bot | grep -q "Logged in as"; then
    echo "✅ Bot connected"
else
    echo "❌ Bot not connected"
    exit 1
fi

echo "✨ All tests passed!"
docker-compose down
```

---

## Additional Resources

- **Docker Compose Docs**: https://docs.docker.com/compose/
- **Litestar Docs**: https://docs.litestar.dev/
- **Discord.py Docs**: https://discordpy.readthedocs.io/
- **uv Docs**: https://docs.astral.sh/uv/

---

## Getting Help

- **GitHub Issues**: https://github.com/JacobCoffee/byte/issues
- **Discord Support**: [Your Discord server link]
- **Documentation**: `/docs` directory in repository

---

**Last Updated**: 2025-11-23 **Version**: 2.0.0 (Phase 2: Docker Compose)
