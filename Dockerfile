# syntax=docker/dockerfile:1

##############################
# Builder stage – install deps
##############################
FROM python:3.11-slim AS builder

# Install Poetry
RUN pip install --no-cache-dir poetry==1.8.2

# Copy only dependency files first for better layer caching
WORKDIR /app
COPY pyproject.toml poetry.lock* ./

# Configure Poetry: no virtualenv creation
ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry'

RUN poetry install --no-interaction --no-ansi --only main

# Copy the rest of the source code
COPY . .

##############################
# Runtime stage – minimal image
##############################
FROM python:3.11-alpine AS runtime

# Create non-root user
RUN addgroup -S app && adduser -S app -G app
USER app

# Copy site-packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app /app

WORKDIR /app

EXPOSE 8000
ENTRYPOINT ["uvicorn"]
CMD ["src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
