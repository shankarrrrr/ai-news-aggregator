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
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy application code first
COPY . .

# Install Python dependencies directly from requirements
RUN pip install --upgrade pip && \
    pip install sqlalchemy psycopg2-binary google-generativeai requests beautifulsoup4 \
    feedparser youtube-transcript-api hypothesis python-dotenv

# Default command (can be overridden)
CMD ["python", "scripts/run_pipeline.py"]
