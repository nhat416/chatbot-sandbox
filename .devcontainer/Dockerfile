FROM python:3.12-slim

# Install system dependencies and OpenCode CLI
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates tar \
    && rm -rf /var/lib/apt/lists/* \
    && curl -fsSL https://opencode.ai/install | bash -s -- --no-modify-path

ENV PATH="/root/.opencode/bin:${PATH}"

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
