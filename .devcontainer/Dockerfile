FROM python:3.12-slim

# Install uv (fast Python package manager)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Set working directory
WORKDIR /workspace

# Copy dependency file first (for Docker layer caching)
COPY pyproject.toml ./

# Install dependencies
RUN uv sync

# Copy the rest of the project
COPY . .

# Expose the FastAPI dev server port
EXPOSE 8000
