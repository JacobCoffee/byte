# syntax=docker/dockerfile:1

# ============================================================================
# Builder Stage: Install dependencies and build virtual environment
# ============================================================================
FROM python:3.12-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
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
COPY services/bot ./services/bot

# Install dependencies with frozen lockfile (no dev dependencies)
# This creates a .venv directory with all dependencies
RUN uv sync --frozen --no-dev --no-editable

# ============================================================================
# Runtime Stage: Minimal production image
# ============================================================================
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN groupadd -r botuser && \
    useradd -r -g botuser -u 1000 -d /app -s /sbin/nologin botuser

# Copy virtual environment from builder stage
COPY --from=builder --chown=botuser:botuser /app/.venv /app/.venv

# Copy application code from builder stage
COPY --from=builder --chown=botuser:botuser /app/services/bot /app/services/bot
COPY --from=builder --chown=botuser:botuser /app/packages/byte-common /app/packages/byte-common

# Copy workspace configuration (needed for uv run commands)
COPY --from=builder --chown=botuser:botuser /app/pyproject.toml /app/uv.lock ./

# Set PATH to use virtual environment binaries
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app"

# Switch to non-root user
USER botuser

# Run the Discord bot
CMD ["python", "-m", "byte_bot"]
