FROM python:alpine

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git

# Copy requirements
COPY pyproject.toml .
# Install dependencies 
RUN pip install -e .

# Copy application code
COPY . .

# Keep container running for development
CMD ["python", "-c", "import time; time.sleep(infinity)"]