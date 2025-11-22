# Byte API Service

REST API service for the Byte Bot application.

## Overview

This service provides the web API and dashboard functionality including:

- Litestar REST API
- Web dashboard with Jinja2 templates
- TailwindCSS + DaisyUI frontend
- Database management and migrations
- Authentication and authorization

## Technology Stack

- Python 3.12+
- Litestar framework
- PostgreSQL (via Advanced Alchemy)
- Jinja2 templates
- TailwindCSS + DaisyUI
- Shared code from `byte-common` package

## Status

**Phase 0.1**: Directory structure created. Implementation pending.

## Future Structure

```
services/api/
├── byte_api/          # API source code
│   ├── domain/        # Domain models
│   ├── lib/           # API utilities
│   ├── templates/     # Jinja2 templates
│   └── static/        # Static assets
├── tests/             # API-specific tests
├── pyproject.toml     # API service configuration
└── Dockerfile         # API service container
```

## Development

To be populated during Phase 0.3 (API Service Migration).
