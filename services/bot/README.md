# Byte Bot Service

Discord bot service for the Byte Bot application.

## Overview

This service handles all Discord-related functionality including:

- Discord bot event handling (on_message, on_guild_join, etc.)
- Slash commands and interactions
- Discord.py plugin system (cogs)
- Discord UI components (views, modals, buttons)
- Integration with Byte API for database operations

## Technology Stack

- **Python**: 3.12+
- **Discord.py**: v2.3.2+
- **HTTP Client**: httpx (for API calls)
- **Settings**: pydantic-settings
- **Shared Code**: `byte-common` package (workspace dependency)

## Project Structure

```
services/bot/
├── src/
│   └── byte_bot/          # Bot source code
│       ├── __init__.py
│       ├── __main__.py    # Entry point
│       ├── bot.py         # Bot class and runner
│       ├── api_client.py  # HTTP client for Byte API
│       ├── config.py      # Bot settings
│       ├── lib/           # Bot infrastructure
│       │   ├── checks.py  # Permission checks
│       │   ├── log.py     # Logging configuration
│       │   ├── utils.py   # Utilities
│       │   ├── common/    # Common resources (links, messages)
│       │   └── types/     # Type definitions (Astral, Python)
│       ├── plugins/       # Discord commands (auto-loaded)
│       │   ├── admin.py   # Admin commands
│       │   ├── config.py  # Configuration commands
│       │   ├── events.py  # Event handlers
│       │   ├── forums.py  # Forum management
│       │   ├── github.py  # GitHub integration
│       │   ├── python.py  # Python documentation lookups
│       │   ├── astral.py  # Astral project lookups
│       │   ├── general.py # General commands
│       │   └── custom/    # Custom plugins (Litestar, etc.)
│       └── views/         # Discord UI components
│           ├── astral.py  # Astral project views
│           ├── config.py  # Configuration modals
│           ├── forums.py  # Forum management views
│           └── python.py  # Python documentation views
├── tests/                 # Bot-specific tests (TODO)
├── pyproject.toml         # Package configuration
├── Dockerfile             # Production container
└── README.md              # This file
```

## Development

### Prerequisites

- Python 3.12+
- uv package manager
- Discord bot token (from Discord Developer Portal)
- Access to Byte API (or run locally)

### Setup

From the **workspace root** (`/byte`):

```bash
# Install all dependencies (including bot service)
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env and set:
# - DISCORD_TOKEN
# - DISCORD_DEV_GUILD_ID
# - DISCORD_DEV_USER_ID
# - API_URL (defaults to http://localhost:8000)
```

### Running Locally

**Option 1: Via workspace command (recommended)**

```bash
# From workspace root
uv run app run-bot
```

**Option 2: Directly via module**

```bash
# From workspace root
uv run python -m byte_bot
```

**Option 3: Via entry point**

```bash
# From workspace root
uv run byte-bot
```

### Configuration

The bot service uses environment variables for configuration. See `src/byte_bot/config.py` for all available settings:

**Required:**

- `DISCORD_TOKEN` - Bot token from Discord Developer Portal

**Optional:**

- `DISCORD_COMMAND_PREFIX` - Command prefix (default: `!`)
- `DISCORD_DEV_GUILD_ID` - Guild ID for slash command sync
- `DISCORD_DEV_USER_ID` - Your Discord user ID
- `DISCORD_PLUGINS_LOC` - Plugin module path (default: `byte_bot.plugins`)
- `API_URL` - Byte API base URL (default: `http://localhost:8000`)
- `LOG_LEVEL` - Logging level (default: `INFO`)
- `LOG_FILE` - Log file path (optional)

### Plugin Development

Plugins are automatically loaded from `byte_bot/plugins/`. To create a new plugin:

```python
# src/byte_bot/plugins/my_plugin.py
from discord.ext import commands
from discord import ApplicationContext


class MyPlugin(commands.Cog):
    """My custom plugin."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(description="My command")
    async def my_command(self, ctx: ApplicationContext):
        """Handle command."""
        await ctx.respond("Hello!")


def setup(bot: commands.Bot):
    """Required for auto-loading."""
    bot.add_cog(MyPlugin(bot))
```

The plugin will be automatically loaded when the bot starts.

## Docker

### Building

From the **workspace root**:

```bash
docker build -f services/bot/Dockerfile -t byte-bot .
```

### Running

```bash
docker run -d \
  --name byte-bot \
  -e DISCORD_TOKEN=your_token_here \
  -e API_URL=http://api:8000 \
  byte-bot
```

### Docker Compose

```yaml
services:
  bot:
    build:
      context: .
      dockerfile: services/bot/Dockerfile
    environment:
      - DISCORD_TOKEN=${DISCORD_TOKEN}
      - API_URL=http://api:8000
    depends_on:
      - api
    restart: unless-stopped
```

## API Integration

The bot service calls the Byte API for database operations. See `src/byte_bot/api_client.py` for available methods:

- `get_guild(guild_id: int)` - Fetch guild configuration
- `create_guild(guild_data: dict)` - Create new guild
- `update_guild(guild_id: str, guild_data: dict)` - Update guild
- `delete_guild(guild_id: str)` - Delete guild

All database operations go through the API - the bot does not directly access the database.

## Testing

```bash
# Run bot service tests (from workspace root)
uv run pytest services/bot/tests
```

## Status

**Phase 1.2**: ✅ Complete

- [x] Bot service extracted from monolith
- [x] All plugins migrated to `services/bot/src/byte_bot/plugins/`
- [x] All views migrated to `services/bot/src/byte_bot/views/`
- [x] API client implemented
- [x] Configuration system set up
- [x] Entry points configured
- [x] Import errors fixed
- [x] Dockerfile created
- [ ] Tests implemented (TODO: Phase 1.3)

## Next Steps

- **Phase 1.3**: Implement comprehensive test suite
- **Phase 2**: Remove old monolith code (`byte_bot/byte/`)
- **Phase 3**: Deploy bot and API services independently

## License

MIT License - See workspace LICENSE file
