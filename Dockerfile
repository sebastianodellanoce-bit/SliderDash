# Dockerfile per Azure Container Apps (opzionale)
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create credentials directory (will be mounted or copied separately)
RUN mkdir -p credentials

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/_stcore/health')" || exit 1

# Run Streamlit
CMD ["python", "-m", "streamlit", "run", "app.py", "--server.port=8000", "--server.address=0.0.0.0", "--server.headless=true", "--browser.gatherUsageStats=false"]

