
FROM astral/uv:python3.12-bookworm-slim AS dependencies

WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock ./

RUN uv sync



# SECRET_KEY is required for Django to run collectstatic
ARG SECRET_KEY=dummy-secret-key-for-build
ENV SECRET_KEY=${SECRET_KEY}
ENV DJANGO_SETTINGS_MODULE=rentease_backend.settings



# Copy application code
COPY . .

EXPOSE 8000

# Run gunicorn
CMD ["uv", "run","gunicorn", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "2", \
     "--threads", "4", \
     "--worker-class", "gthread", \
     "--worker-tmp-dir", "/dev/shm", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--capture-output", \
     "--enable-stdio-inheritance", \
     "rentease_backend.wsgi:application"]