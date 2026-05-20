# Build stage
FROM python:3.12 AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT=/usr/local

# Set the working directory in the container
WORKDIR /app

# Install system dependencies, including gettext
RUN apt-get update && apt-get install -y \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Copy only pyproject.toml and uv.lock (if it exists)
COPY pyproject.toml uv.lock* ./

# Install project dependencies into the system Python
RUN uv sync --frozen --no-install-project --no-dev

# Copy the project code into the container
COPY . .

# Ensure the env variables are present -- although they won't be used
# during the build, they need to be set.
COPY .env.example .env

# Install the project itself
RUN uv sync --frozen --no-dev

# Collect static files
RUN make sass
RUN python manage.py collectstatic --noinput

# Compile translations
RUN python manage.py compilemessages

# Run stage
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Set the working directory in the container
WORKDIR /app

# Copy the installed dependencies and project files from the builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

# Expose the port the app runs on
EXPOSE ${PORT}

# Start the application
CMD gunicorn --bind 0.0.0.0:${PORT} web.wsgi:application
