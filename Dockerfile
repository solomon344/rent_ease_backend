# Multi-stage Dockerfile for RentEase Backend
# Uses uv package manager for fast, reliable dependency installation

# ============================================
# Stage 1: Dependencies
# ============================================
FROM astral/uv:python3.12-bookworm-slim AS dependencies

WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock ./

# Install dependencies to a virtual environment
RUN uv sync --frozen --no-dev --no-install-workspace --no-editable

# ============================================
# Stage 2: Builder (for collecting static files)
# ============================================
FROM astral/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

# Copy the virtual environment from dependencies stage
COPY --from=dependencies /app/.venv /app/.venv

# Copy project files
COPY . .

# Collect static files using uv run
RUN uv run --frozen python manage.py collectstatic --noinput

# ============================================
# Stage 3: Runtime
# ============================================
FROM python:3.12-slim-bookworm AS runtime

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Required for some Python packages
    libpq5 \
    # For health checks
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get purge -y --auto-remove \
    && mkdir -p /app

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Copy virtual environment from dependencies stage
COPY --from=dependencies /app/.venv /app/.venv

# Copy static files from builder stage
COPY --from=builder /app/staticfiles /app/staticfiles

# Copy application code
COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE="rentease_backend.settings"

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/ || exit 1

# Run gunicorn
CMD ["gunicorn", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "2", \
     "--threads", "4", \
     "--worker-class", "gthread", \
     "--worker-tmp-dir", "/dev/shm", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--capture-output", \
     "--enable-stdio-inheritance", \
     "rent_ease_backend.wsgi:application"]