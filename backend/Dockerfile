# Stage 1: Builder
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

# Set environment variables for uv
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PYTHON=python3.12

WORKDIR /app

# Install dependencies first for better caching
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Copy the rest of the application source
COPY . .

# Sync the project
RUN uv sync --frozen --no-dev

# Stage 2: Runner
FROM python:3.12-slim-bookworm

# Install curl and libmagic for healthchecks and file validation
RUN apt-get update && apt-get install -y --no-install-recommends curl libmagic1 && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user and group
RUN groupadd -r app && useradd -r -g app app

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create necessary directories and set ownership
RUN mkdir -p /app/data /app/static/images && \
    chown -R app:app /app

# Copy the virtual environment and application code from the builder stage
COPY --from=builder --chown=app:app /app /app

# Switch to non-root user
USER app

# Expose the application port
EXPOSE 8000

# Start the application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
