# Use official Python 3.11 slim image
FROM python:3.11-slim

# Install uv for package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock .python-version ./

# Install dependencies using uv
RUN uv sync --frozen

# Copy source code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Set entrypoint to run the simulation
ENTRYPOINT ["uv", "run", "python", "main.py"]
CMD ["run", "--config", "config/world_v1.json", "--viz", "none"]
