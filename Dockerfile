# Use an official lightweight Python image
FROM python:3.12-slim

# Install system dependencies and Poetry
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    git \
    libffi-dev \
    libpq-dev \
    postgresql-client \
    --no-install-recommends && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set PATH to include Poetry
ENV PATH="/root/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy only the dependency files first (to leverage Docker cache)
COPY pyproject.toml poetry.lock ./

ENV PYTHONPATH=/app
ENV PIPENV_VENV_IN_PROJECT=1

# Install dependencies using Poetry
RUN poetry install --no-root  --only main

# Copy everything including the Alembic setup + start.sh
COPY . .

# Make sure start.sh is executable
RUN chmod +x ./start.sh

# Expose port for FastAPI
EXPOSE 8000

# Use start.sh as the entrypoint
CMD ["./start.sh"]
