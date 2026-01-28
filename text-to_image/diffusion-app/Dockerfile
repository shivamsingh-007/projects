# Production-Ready Dockerfile for Stable Diffusion Image Generator
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY frontend/ ./frontend/

# Create models directory
RUN mkdir -p models

# Pre-download models at build time (optional - reduces first run time)
# Uncomment the following lines to download models during build
# This will increase image size but eliminate first-run download wait
# RUN python -c "from diffusers import StableDiffusionPipeline; \
#     StableDiffusionPipeline.from_pretrained('stabilityai/stable-diffusion-2-1-base', cache_dir='./models')"

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV TRANSFORMERS_CACHE=/app/models
ENV HF_HOME=/app/models

# Run the application
CMD ["python", "app.py"]
