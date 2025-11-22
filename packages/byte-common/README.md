# Byte Common Package

Shared code package for all Byte Bot services.

## Overview

This package contains shared utilities, models, and configurations used across all Byte Bot services (bot, api, worker).

## Contents

The package will include:

- **Models**: Shared Pydantic models and database schemas
- **Configuration**: Environment configuration and settings
- **Utilities**: Common helper functions and utilities
- **Constants**: Shared constants and enums
- **Types**: Shared type definitions
- **Database**: Shared database models and migrations

## Technology Stack

- Python 3.12+
- Pydantic for models
- Pydantic Settings for configuration
- Advanced Alchemy for database models

## Status

**Phase 0.2**: Package implementation complete. All core modules extracted.

## Structure

```
packages/byte-common/
├── src/
│   └── byte_common/
│       ├── __init__.py
│       ├── models/              # SQLAlchemy database models
│       │   ├── __init__.py
│       │   ├── guild.py
│       │   ├── github_config.py
│       │   ├── forum_config.py
│       │   ├── sotags_config.py
│       │   ├── allowed_users_config.py
│       │   └── user.py
│       ├── schemas/             # Pydantic schemas for API
│       │   ├── __init__.py
│       │   ├── guild.py
│       │   └── github.py
│       ├── settings/            # Settings base classes
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── database.py
│       ├── clients/             # External service clients
│       │   ├── __init__.py
│       │   └── github.py
│       ├── utils/               # Shared utilities
│       │   ├── __init__.py
│       │   ├── strings.py
│       │   └── encoding.py
│       └── constants.py         # Shared constants
├── tests/                       # Package tests (TODO)
├── pyproject.toml               # Package configuration
└── README.md                    # This file
```

## Development

This package was created in Phase 0.2 by extracting shared code from the existing monolith.

## Usage

Services will depend on this package in their `pyproject.toml`:

```toml
dependencies = [
    "byte-common",
    # ... other dependencies
]
```
