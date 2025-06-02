# SuperSmartMatch V2 Dockerfile
# Optimized for production deployment on port 5070

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash supersmartmatch
RUN chown -R supersmartmatch:supersmartmatch /app
USER supersmartmatch

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5070/health || exit 1

# Expose port 5070
EXPOSE 5070

# Set default command
CMD ["python", "main.py"]

# Alternative commands:
# For development: CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5070", "--reload"]
# For production: CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:5070"]
