FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ENV=production

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml .

# Install Python dependencies
RUN pip install --upgrade pip && pip install .

# Copy application code
COPY . .

# Default command (can be overridden)
CMD ["python", "scripts/run_pipeline.py"]
