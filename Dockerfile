# --- Build stage ---
FROM python:3.12-slim AS build
WORKDIR /src
COPY backend/pyproject.toml backend/
COPY backend/app backend/app
RUN pip install --no-cache-dir --prefix=/install ./backend

# --- Runtime stage ---
FROM python:3.12-slim

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Copy installed packages
COPY --from=build /install /usr/local

# Copy application code
COPY backend/app /srv/app
COPY data /srv/data

WORKDIR /srv

# Switch to non-root user
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request as u; u.urlopen('http://localhost:8000/healthz')"

# Run with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
