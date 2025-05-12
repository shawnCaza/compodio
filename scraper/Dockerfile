FROM python:3.11.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    ffmpeg \
    git \
    libxml2-dev \
    libxslt-dev \
    python3-dev \
    gcc \
    g++ \
    build-essential \
    default-mysql-client \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml .
# Install dependencies 
RUN pip install -e .

# Copy application code
COPY . .

# Keep container running for development
CMD ["tail", "-f", "/dev/null"]