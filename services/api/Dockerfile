# syntax=docker/dockerfile:1

# ============================================================================
# Builder Stage: Install dependencies and build virtual environment
# ============================================================================
FROM python:3.14-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy uv binary from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set uv environment variables for optimal performance
ENV UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Copy workspace configuration files
COPY pyproject.toml uv.lock ./

# Copy shared packages and service code
COPY packages/byte-common ./packages/byte-common
COPY services/api ./services/api

# Install dependencies with frozen lockfile (no dev dependencies)
# This creates a .venv directory with all dependencies
RUN uv sync --frozen --no-dev --no-editable

# ============================================================================
# Runtime Stage: Minimal production image
# ============================================================================
FROM python:3.14-slim

# Set working directory
WORKDIR /app

# Install runtime system dependencies (PostgreSQL client library)
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r appuser && \
    useradd -r -g appuser -u 1000 -d /app -s /sbin/nologin appuser

# Copy virtual environment from builder stage
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy application code from builder stage
COPY --from=builder --chown=appuser:appuser /app/services/api /app/services/api
COPY --from=builder --chown=appuser:appuser /app/packages/byte-common /app/packages/byte-common

# Copy workspace configuration (needed for uv run commands)
COPY --from=builder --chown=appuser:appuser /app/pyproject.toml /app/uv.lock ./

# Set PATH to use virtual environment binaries
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app"

# Expose API port
EXPOSE 8000

# Switch to non-root user
USER appuser

# Health check to ensure service is responsive
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run database migrations and start server
# Note: In production, consider running migrations separately in an init container
CMD ["sh", "-c", "alembic upgrade head && uvicorn byte_api.app:app --host 0.0.0.0 --port 8000 --workers 2"]
