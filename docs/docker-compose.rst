==========================
Docker Compose Development
==========================

This document describes how to use Docker Compose for local development of the Byte Bot project.

Overview
========

The project provides Docker Compose configurations for two development scenarios:

1. **Full Stack** (``docker-compose.yml``) - PostgreSQL + API Service + Bot Service
2. **Infrastructure Only** (``docker-compose.infra.yml``) - PostgreSQL only (for running services locally)

This setup enables developers to:

- Spin up the entire stack with a single command
- Get hot-reload for both API and Bot services
- Develop without installing PostgreSQL locally
- Test service-to-service communication
- Isolate development environments

Architecture
============

Full Stack Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    ┌─────────────────────────────────────────────────────────┐
    │                   Docker Compose Stack                   │
    │                                                          │
    │  ┌──────────────┐    ┌──────────────┐   ┌───────────┐ │
    │  │  PostgreSQL  │◄───│  API Service │◄──│Bot Service│ │
    │  │  Container   │    │  Container   │   │ Container │ │
    │  │              │    │              │   │           │ │
    │  │ postgres:15  │    │ Hot-reload   │   │Hot-reload │ │
    │  │              │    │ enabled      │   │enabled    │ │
    │  └──────┬───────┘    └──────┬───────┘   └─────┬─────┘ │
    │         │                   │                 │        │
    │         │                   │                 │        │
    │  ┌──────▼───────────────────▼─────────────────▼──────┐ │
    │  │           Shared byte-network Bridge             │ │
    │  └──────────────────────────────────────────────────┘ │
    │                                                          │
    │  Volume Mounts (hot-reload):                            │
    │  - ./services/api/src → /app/services/api/src          │
    │  - ./services/bot/src → /app/services/bot/src          │
    │  - ./packages/byte-common → /app/packages/byte-common  │
    └─────────────────────────────────────────────────────────┘

Services
--------

**PostgreSQL**:
  - Image: ``postgres:15-alpine``
  - Port: ``5432:5432``
  - Database: ``byte``
  - Credentials: ``byte:bot``
  - Health check: ``pg_isready``
  - Persistent volume: ``pgdata``

**API Service**:
  - Build: ``services/api/Dockerfile``
  - Port: ``8000:8000``
  - Framework: Litestar (ASGI)
  - Command: ``uvicorn`` with ``--reload``
  - Depends on: PostgreSQL (waits for health check)
  - Hot-reload: Enabled via volume mounts

**Bot Service**:
  - Build: ``services/bot/Dockerfile``
  - Framework: discord.py
  - Depends on: API service (waits for health check)
  - API URL: ``http://api:8000``
  - Hot-reload: Enabled via volume mounts

Prerequisites
=============

Required
~~~~~~~~

- Docker Engine 20.10+
- Docker Compose v2.0+
- ``.env`` file with required credentials (see `.env.example`)

.. important::
   Docker Compose v2 uses ``docker compose`` (space) instead of ``docker-compose`` (hyphen).
   All commands in this guide use the v2 syntax.

Optional for Bot Service
~~~~~~~~~~~~~~~~~~~~~~~~~

If you want the bot to connect to Discord, you need:

- ``DISCORD_TOKEN`` - Bot token from Discord Developer Portal
- ``DISCORD_DEV_GUILD_ID`` - Guild ID for slash command sync (optional)
- ``DISCORD_DEV_USER_ID`` - Your Discord user ID (optional)

Without these, the bot container will fail to start, but PostgreSQL and API services will run normally.

Quick Start
===========

1. **Clone the repository**:

   .. code-block:: bash

      git clone https://github.com/JacobCoffee/byte.git
      cd byte

2. **Create environment file**:

   .. code-block:: bash

      cp .env.example .env
      # Edit .env with your credentials (at minimum, DISCORD_TOKEN if running bot)

3. **Start all services**:

   .. code-block:: bash

      make docker-up

   This will:

   - Build Docker images for API and Bot services
   - Start PostgreSQL container
   - Run database migrations
   - Start API service on http://localhost:8000
   - Start Bot service (if ``DISCORD_TOKEN`` is set)

4. **View logs**:

   .. code-block:: bash

      make docker-logs

5. **Stop all services**:

   .. code-block:: bash

      make docker-down

Makefile Commands
=================

The project includes comprehensive Makefile targets for Docker Compose operations:

Starting Services
~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Command
     - Description
   * - ``make docker-up``
     - Start all services (PostgreSQL, API, Bot)
   * - ``make infra-up``
     - Start only PostgreSQL (for running services locally)

Stopping Services
~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Command
     - Description
   * - ``make docker-down``
     - Stop all services (keeps volumes)
   * - ``make docker-down-volumes``
     - Stop all services and remove volumes (deletes database data)
   * - ``make infra-down``
     - Stop PostgreSQL infrastructure

Viewing Logs
~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Command
     - Description
   * - ``make docker-logs``
     - Follow logs from all services
   * - ``make docker-logs-api``
     - Follow logs from API service only
   * - ``make docker-logs-bot``
     - Follow logs from bot service only
   * - ``make docker-logs-postgres``
     - Follow logs from PostgreSQL only

Shell Access
~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Command
     - Description
   * - ``make docker-shell-api``
     - Open bash shell in API container
   * - ``make docker-shell-bot``
     - Open bash shell in bot container
   * - ``make docker-shell-postgres``
     - Open PostgreSQL shell (``psql``)

Service Management
~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Command
     - Description
   * - ``make docker-ps``
     - Show status of all services
   * - ``make docker-restart``
     - Restart all services
   * - ``make docker-restart-api``
     - Restart API service only
   * - ``make docker-restart-bot``
     - Restart bot service only
   * - ``make docker-rebuild``
     - Rebuild and restart all services (force recreate)

Direct Docker Compose Commands
===============================

You can also use ``docker compose`` directly for more control:

.. code-block:: bash

   # Start services in foreground (see logs directly)
   docker compose up

   # Start specific service
   docker compose up api

   # Build without starting
   docker compose build

   # View service status
   docker compose ps

   # Stop specific service
   docker compose stop bot

   # Remove stopped containers
   docker compose rm

   # View resource usage
   docker compose stats

Development Workflow
====================

Typical Daily Workflow
~~~~~~~~~~~~~~~~~~~~~~

1. **Start your development day**:

   .. code-block:: bash

      make docker-up

2. **Check that services are running**:

   .. code-block:: bash

      make docker-ps

   Expected output:

   .. code-block:: text

      NAME           IMAGE              STATUS          PORTS
      byte-postgres  postgres:15-alpine Up 2 minutes    0.0.0.0:5432->5432/tcp
      byte-api       byte-api           Up 2 minutes    0.0.0.0:8000->8000/tcp
      byte-bot       byte-bot           Up 1 minute

3. **Make code changes** in ``services/api/src`` or ``services/bot/src``

   - Changes are automatically detected (hot-reload enabled)
   - Services restart automatically
   - No need to rebuild containers

4. **View logs as you develop**:

   .. code-block:: bash

      # All services
      make docker-logs

      # Or specific service
      make docker-logs-api

5. **Access API documentation**:

   Open http://localhost:8000/api/swagger in your browser

6. **End your development session**:

   .. code-block:: bash

      make docker-down

Working with Database
~~~~~~~~~~~~~~~~~~~~~

**Connect with psql**:

.. code-block:: bash

   make docker-shell-postgres

**Run migrations**:

Migrations run automatically when the API service starts. To run manually:

.. code-block:: bash

   make docker-shell-api
   # Inside container:
   alembic upgrade head

**Create new migration**:

.. code-block:: bash

   make docker-shell-api
   # Inside container:
   alembic revision --autogenerate -m "description"

**Reset database** (deletes all data):

.. code-block:: bash

   make docker-down-volumes
   make docker-up

Debugging Services
~~~~~~~~~~~~~~~~~~

**API service not responding**:

1. Check logs:

   .. code-block:: bash

      make docker-logs-api

2. Verify health:

   .. code-block:: bash

      curl http://localhost:8000/health

3. Shell into container:

   .. code-block:: bash

      make docker-shell-api
      # Check environment
      env | grep DB_URL
      # Test database connection
      python -c "from byte_api.lib.db.orm import DatabaseManager; print('OK')"

**Bot not connecting**:

1. Check Discord token is set:

   .. code-block:: bash

      grep DISCORD_TOKEN .env

2. View bot logs:

   .. code-block:: bash

      make docker-logs-bot

3. Verify API connectivity:

   .. code-block:: bash

      make docker-shell-bot
      # Inside container:
      curl http://api:8000/health

**PostgreSQL issues**:

1. Check health:

   .. code-block:: bash

      docker compose exec postgres pg_isready -U byte

2. View logs:

   .. code-block:: bash

      make docker-logs-postgres

3. Reset database:

   .. code-block:: bash

      make docker-down-volumes
      make infra-up

Infrastructure-Only Mode
========================

For developers who prefer to run services outside Docker (e.g., in their IDE):

1. **Start only PostgreSQL**:

   .. code-block:: bash

      make infra-up

2. **Configure services to connect**:

   In your ``.env`` file:

   .. code-block:: bash

      DB_URL=postgresql+asyncpg://byte:bot@localhost:5432/byte

3. **Run services locally**:

   .. code-block:: bash

      # Terminal 1: API service
      uv run app run-web --reload

      # Terminal 2: Bot service
      uv run app run-bot

4. **Stop PostgreSQL when done**:

   .. code-block:: bash

      make infra-down

This mode is useful for:

- Debugging in your IDE with breakpoints
- Running services with different Python versions
- Testing without containerization overhead

Hot Reload
==========

How It Works
~~~~~~~~~~~~

Both API and Bot services have hot-reload enabled through volume mounts:

.. code-block:: yaml

   volumes:
     - ./services/api/src:/app/services/api/src:delegated
     - ./packages/byte-common:/app/packages/byte-common:delegated

When you edit files in these directories on your host machine, the changes are immediately
reflected inside the container. The services detect changes and restart automatically.

Supported Changes
~~~~~~~~~~~~~~~~~

**API Service** (uvicorn with ``--reload``):
  - Python files (``.py``) in ``services/api/src/``
  - Shared code in ``packages/byte-common/``
  - Automatic restart on detection

**Bot Service** (discord.py plugin reload):
  - Bot plugins in ``services/bot/src/byte_bot/plugins/``
  - Shared code in ``packages/byte-common/``
  - Automatic reload via discord.py's extension reload

Requires Rebuild
~~~~~~~~~~~~~~~~

Changes to these files require rebuilding containers:

- ``pyproject.toml`` (new dependencies)
- ``uv.lock`` (updated lockfile)
- ``Dockerfile`` changes
- System package requirements

To rebuild:

.. code-block:: bash

   make docker-rebuild

Configuration
=============

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

The Docker Compose setup uses environment variables from ``.env`` file:

**Required for API**:

.. code-block:: bash

   DB_URL=postgresql+asyncpg://byte:bot@postgres:5432/byte
   SECRET_KEY=your-secret-key-here

**Required for Bot**:

.. code-block:: bash

   DISCORD_TOKEN=your-discord-bot-token
   API_SERVICE_URL=http://api:8000

**Optional**:

.. code-block:: bash

   # Discord
   DISCORD_DEV_GUILD_ID=123456789012345678
   DISCORD_DEV_USER_ID=123456789012345678

   # GitHub (for issue creation)
   GITHUB_APP_ID=123456
   GITHUB_APP_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n..."
   GITHUB_APP_CLIENT_ID=Iv1.abc123
   GITHUB_APP_CLIENT_SECRET=abc123

   # Logging
   LOG_LEVEL=10  # DEBUG
   ENVIRONMENT=dev

Docker Compose Files
~~~~~~~~~~~~~~~~~~~~

**docker-compose.yml** (Full Stack):

- Defines PostgreSQL, API, and Bot services
- Sets up networking and volume mounts
- Configures health checks and dependencies
- Enables hot-reload for development

**docker-compose.infra.yml** (Infrastructure Only):

- Minimal PostgreSQL configuration
- No service dependencies
- Useful for local development outside Docker

Customization
~~~~~~~~~~~~~

To customize the setup, edit ``docker-compose.yml``:

**Change API port**:

.. code-block:: yaml

   api:
     ports:
       - "8080:8000"  # Host:Container

**Add more workers**:

.. code-block:: yaml

   api:
     command: sh -c "alembic upgrade head && uvicorn byte_api.app:create_app --factory --reload --host 0.0.0.0 --port 8000 --workers 4"

**Mount additional volumes**:

.. code-block:: yaml

   api:
     volumes:
       - ./services/api/src:/app/services/api/src:delegated
       - ./my-custom-config:/app/config:ro  # Read-only

Troubleshooting
===============

Port Conflicts
~~~~~~~~~~~~~~

**Error**: ``Bind for 0.0.0.0:5432 failed: port is already allocated``

**Solution**: Another PostgreSQL instance is running on port 5432.

.. code-block:: bash

   # Check what's using the port
   lsof -i :5432

   # Option 1: Stop local PostgreSQL
   brew services stop postgresql@15

   # Option 2: Change port in docker-compose.yml
   ports:
     - "5433:5432"  # Use different host port

Permission Errors
~~~~~~~~~~~~~~~~~

**Error**: ``Permission denied`` when mounting volumes

**Solution**: Docker Desktop may need permission to access directories.

- On macOS: System Preferences → Security & Privacy → Files and Folders → Docker
- On Linux: Ensure your user is in the ``docker`` group: ``sudo usermod -aG docker $USER``

Container Build Failures
~~~~~~~~~~~~~~~~~~~~~~~~~

**Error**: ``failed to solve: failed to compute cache key``

**Solution**: Clear Docker cache and rebuild:

.. code-block:: bash

   docker system prune -a
   make docker-rebuild

Database Connection Refused
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Error**: ``could not connect to server: Connection refused``

**Solution**: PostgreSQL container may not be healthy yet.

.. code-block:: bash

   # Check PostgreSQL health
   docker compose ps postgres

   # View startup logs
   make docker-logs-postgres

   # Wait for health check to pass (usually 10-20 seconds)

Service Won't Start
~~~~~~~~~~~~~~~~~~~

**Error**: Service exits immediately after starting

**Solution**: Check logs for errors:

.. code-block:: bash

   make docker-logs-api  # or docker-logs-bot

   # Common issues:
   # 1. Missing environment variables
   # 2. Invalid credentials
   # 3. Port already in use

Best Practices
==============

Development
~~~~~~~~~~~

1. **Always use ``.env`` file** for credentials (never commit secrets)
2. **Use ``make docker-logs`` in a separate terminal** to monitor services
3. **Run ``make docker-ps`` periodically** to ensure services are healthy
4. **Use ``make docker-rebuild``** after dependency changes
5. **Stop services when not in use** to free up resources

Production Considerations
~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::
   The provided Docker Compose setup is for **development only**.
   Do not use this configuration in production.

For production:

- Use separate, production-optimized Dockerfiles
- Disable hot-reload and debug mode
- Use proper secret management (not ``.env`` files)
- Set up SSL/TLS termination
- Configure proper resource limits
- Use Docker secrets or Kubernetes ConfigMaps
- Run migrations separately (not on container startup)

Performance
~~~~~~~~~~~

**Slow hot-reload on macOS**:

The ``:delegated`` mount option improves performance on macOS by relaxing
consistency guarantees. If you experience slow file sync:

.. code-block:: yaml

   volumes:
     - ./services/api/src:/app/services/api/src:cached  # Try 'cached' instead

**High resource usage**:

.. code-block:: bash

   # Check resource consumption
   docker compose stats

   # Reduce workers in docker-compose.yml
   command: uvicorn ... --workers 1  # Instead of 2

Additional Resources
====================

- `Docker Compose Documentation <https://docs.docker.com/compose/>`_
- `Database Migrations Guide <database-migrations.html>`_
- `Litestar Documentation <https://docs.litestar.dev/>`_
- `discord.py Documentation <https://discordpy.readthedocs.io/>`_

See Also
========

- :doc:`database-migrations` - Working with Alembic migrations
- :doc:`contribution-guide` - Contributing to the project
- ``.env.example`` - Environment variable template
- ``services/api/README.md`` - API service details
- ``services/bot/README.md`` - Bot service details
