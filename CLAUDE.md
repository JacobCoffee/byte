# Byte Bot - Development Guide

> **Version**: 0.3.0 (Phase 2 - Microservices) **Python**: 3.13 **Architecture**: Microservices (uv workspace)
> **Updated**: 2025-11-23

---

## ⚡ Critical Rules

1. **NEVER work on main branch** - Always use feature branches via `git worktree` but using `make worktree` command from
   makefile!
2. **ALWAYS ensure you write tests** for changes!
3. **ALWAYS run `make ci`** before committing - Must pass (lint + type-check + fmt + test)
4. **ALWAYS use `uv run`** for Python - Never call `python`/`python3` directly
5. **ALWAYS update docs/** for user-facing changes - Sphinx RST format
6. **ALWAYS create atomic commits** - Small, focused, reviewable
7. **Use prek, not pre-commit** - Git hooks configured with prek
8. **Dispatch subagents for complex tasks** - `ui-engineer`, `python-backend`, `software-architect`,
   `documentation-expert`

- Ready-to-use .env is at /Users/coffee/git/public/JacobCoffee/byte/ with loaded values.
- `make worktree` automatically copies `.claude/settings.local.json` and `.env` to new worktrees.

---

## 🏗️ Architecture (Post-Phase 2)

**uv Workspace** with 3 members:

```
workspace root (pyproject.toml)
├── packages/byte-common      # Shared models, schemas, utils
├── services/api             # Litestar REST API + web dashboard
└── services/bot             # discord.py bot
```

**Runtime**:

- **Docker Compose** (recommended): All services + PostgreSQL in containers
- **Local**: Services run separately, PostgreSQL in Docker via `make infra-up`

**Communication**:

- Bot → API via HTTP (`byte_bot/api_client.py`)
- API → PostgreSQL (direct SQLAlchemy)
- Shared code via `byte-common` package

---

## 🚀 Quick Start Commands

### Setup

```bash
# Full install (backend + frontend + prek hooks)
make install

# Docker development (PRIMARY workflow)
make docker-up          # Start all services
make docker-logs        # Follow logs
make docker-down        # Stop all services
```

### Development

```bash
# Local development (alternative)
make infra-up           # Start PostgreSQL only
make run-dev-server     # Terminal 1: Litestar API (hot-reload)
make run-dev-bot        # Terminal 2: Discord bot
make run-dev-frontend   # Terminal 3: TailwindCSS watcher

# Quality checks (MUST PASS before commit)
make ci                 # Run all checks

# Individual checks
make lint               # prek hooks (ruff + codespell)
make fmt                # Ruff format
make type-check         # ty type checker
make test               # pytest with coverage
```

### Database

```bash
# Migrations (from services/api/)
cd services/api
uv run alembic revision --autogenerate -m "description"
make migrate            # Apply migrations

# Container management
make refresh-container  # Wipe DB, migrate, load test data
```

### Docker Utilities

```bash
make docker-rebuild     # Force rebuild all services
make docker-shell-api   # Enter API container shell
make docker-shell-bot   # Enter bot container shell
make docker-shell-postgres  # PostgreSQL shell
```

---

## 📁 Project Structure (Essential Paths)

```
byte/
├── pyproject.toml              # Workspace root config
├── Makefile                    # Primary automation (280 lines)
├── docker-compose.yml          # Development environment
│
├── packages/byte-common/       # Shared package
│   ├── src/byte_common/
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── schemas/           # Pydantic API schemas
│   │   └── utils.py
│   └── pyproject.toml
│
├── services/api/               # Litestar web service
│   ├── src/byte_api/
│   │   ├── app.py             # create_app() factory
│   │   ├── domain/            # Business logic (guilds, github, system, web)
│   │   └── lib/               # Infrastructure (db, settings, openapi, etc.)
│   │       └── db/migrations/ # Alembic migrations
│   ├── Dockerfile
│   └── pyproject.toml
│
├── services/bot/               # Discord bot service
│   ├── src/byte_bot/
│   │   ├── bot.py             # Bot class, run_bot()
│   │   ├── api_client.py      # HTTP client to API service
│   │   ├── plugins/           # Discord commands (auto-loaded)
│   │   └── views/             # Discord UI components
│   ├── Dockerfile
│   └── pyproject.toml
│
├── tests/                      # Integration + unit tests
├── docs/                       # Sphinx documentation (RST)
│   └── conf.py
└── worktrees/                  # Git worktrees (keep in repo)
```

---

## 🔧 Technology Stack

| Component                | Tool                              | Notes                                 |
| ------------------------ | --------------------------------- | ------------------------------------- |
| **Package Manager (PY)** | uv                                | Fast, PEP 517 build backend           |
| **Package Manager (JS)** | bun                               | Fast JavaScript runtime & package manager |
| **Linting (Python)**     | ruff                              | Replaces black, flake8, isort         |
| **Linting (JS/TS)**      | Biome                             | Fast formatter & linter (replaces Prettier) |
| **Type Checking**        | ty                                | Type checks all services and packages |
| **Testing**              | pytest + pytest-asyncio           | Coverage required                     |
| **Git Hooks**            | prek                              | NOT pre-commit                        |
| **Web Framework**        | Litestar 2.4.3+                   | ASGI, OpenAPI, Jinja2                 |
| **Discord Bot**          | discord.py 2.3.2+                 | Slash commands, views                 |
| **ORM**                  | SQLAlchemy 2.0 + Advanced Alchemy | Async, repository pattern             |
| **Database**             | PostgreSQL 15+                    | Via Docker or Railway                 |
| **Frontend**             | TailwindCSS + DaisyUI             | Compiled via separate watcher         |

**Documentation**: Sphinx, Context7 MCP, allowed WebFetch domains:

- `docs.astral.sh` (uv docs)
- `docs.litestar.dev` (Litestar framework)
- `discordpy.readthedocs.io` (discord.py)

---

## 🔄 Git Workflow

### Branching with Worktrees (REQUIRED for parallel work)

```bash
# Create feature branch in worktree (automated)
make worktree
# OR manually:
git checkout main && git pull
git worktree add worktrees/feature-name -b feature/feature-name

# Work in worktree
cd worktrees/feature-name
# ... make atomic commits ...

# Cleanup after merge
cd ../..
git worktree remove worktrees/feature-name

# Clean up stale worktrees
make worktree-prune
# OR: git worktree prune -v
```

### Commit Standards

- **Atomic commits**: One logical change per commit
- **Conventional commits**: `feat:`, `fix:`, `docs:`, `refactor:`, etc.
- **Examples**:
  - ✅ `feat: add guild caching to API client`
  - ✅ `fix: handle missing Discord token gracefully`
  - ❌ `feat: complete Phase 3 migration` (too large)

### PR Workflow

```bash
# Ensure CI passes locally
make ci

# Create PR via gh CLI
gh pr create --title "feat: description" --body "..."

# Check PR status
gh pr checks
```

---

## 🐛 Common Issues

| Issue                            | Solution                                                       |
| -------------------------------- | -------------------------------------------------------------- |
| **Bot not responding**           | Check `DISCORD_TOKEN`, `DISCORD_DEV_GUILD_ID` in `.env`        |
| **Import errors**                | Run `uv sync` to install dependencies                          |
| **Database connection errors**   | Ensure PostgreSQL running: `make infra-up` or `make docker-up` |
| **Migrations failing**           | Check DB connection, try `make refresh-container`              |
| **Frontend styles not updating** | Restart `make run-dev-frontend` watcher                        |
| **Docker build fails**           | Try `make docker-rebuild`                                      |

---

## 📝 Development Patterns

### Environment Variables

Key variables in `.env`:

- `DISCORD_TOKEN` - Bot token from Discord Developer Portal
- `DB_URL` - PostgreSQL connection (format: `postgresql+asyncpg://user:pass@host:port/db`)
- `SECRET_KEY` - API secret for JWT/sessions
- `GITHUB_APP_*` - GitHub App credentials (ID, private key, client ID/secret)

### Code Style (Enforced by `make ci`)

- **Line length**: 120 characters
- **Type hints**: Required (modern union syntax: `str | None`)
- **Docstrings**: Google style (enforced by ruff)
- **Async**: Use `async`/`await` (SQLAlchemy 2.0 async mode)

### Testing

```python
# Tests in tests/ directory
# Markers: @pytest.mark.unit, @pytest.mark.integration
# Async tests: @pytest.mark.asyncio (auto-enabled)
```

### Database Models

- **Location**: `packages/byte-common/src/byte_common/models/`
- **Migrations**: `cd services/api && uv run alembic revision --autogenerate -m "msg"`
- **Apply**: `make migrate`

### Bot Plugins

- **Location**: `services/bot/src/byte_bot/plugins/`
- **Auto-loaded**: Place `*.py` files, add `def setup(bot)` function
- **Example**: See `plugins/admin.py`, `plugins/github.py`

---

## 🤖 Subagent Coordination

When dispatching subagents:

1. **Create separate worktrees** for each agent
2. **Assign clear boundaries** (files/modules)
3. **Coordinate via git commits** (atomic, descriptive)
4. **Merge incrementally** (review each commit)

**Available agents**:

- `ui-engineer` - Frontend, TailwindCSS, Jinja2 templates
- `python-backend` - API, database, business logic
- `software-architect` - System design, refactoring
- `documentation-expert` - Sphinx docs, API references, tutorials

---

## 📚 Resources

- **Project Docs**: `docs/` (Sphinx RST format)
- **Docker Guide**: `docs/docker-setup.md`
- **API Docs (Scalar)**: http://localhost:8000/api/scalar (default, modern UI)
- **API Docs (Swagger)**: http://localhost:8000/api/swagger (fallback)
- **External**:
  - discord.py: https://discordpy.readthedocs.io/
  - Litestar: https://docs.litestar.dev/
  - uv: https://docs.astral.sh/uv/

---

**Repository**: https://github.com/JacobCoffee/byte
