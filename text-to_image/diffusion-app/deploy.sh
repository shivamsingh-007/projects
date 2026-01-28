#!/bin/bash

# AI Image Generator - Deployment Script
# This script automates the deployment process

set -e

echo "🚀 AI Image Generator - Deployment Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker found${NC}"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}⚠ Docker Compose not found. Will use docker commands instead.${NC}"
    USE_COMPOSE=false
else
    echo -e "${GREEN}✓ Docker Compose found${NC}"
    USE_COMPOSE=true
fi

# Check for NVIDIA GPU
if command -v nvidia-smi &> /dev/null; then
    echo -e "${GREEN}✓ NVIDIA GPU detected${NC}"
    GPU_AVAILABLE=true
else
    echo -e "${YELLOW}⚠ No NVIDIA GPU detected. Will run on CPU (slower).${NC}"
    GPU_AVAILABLE=false
fi

# Create models directory
mkdir -p models
echo -e "${GREEN}✓ Created models directory${NC}"

# Build the Docker image
echo ""
echo "📦 Building Docker image..."
docker build -t ai-image-generator . || {
    echo -e "${RED}❌ Failed to build Docker image${NC}"
    exit 1
}
echo -e "${GREEN}✓ Docker image built successfully${NC}"

# Deployment options
echo ""
echo "🎯 Deployment Options:"
echo "1. Run with Docker Compose (recommended)"
echo "2. Run with Docker command (GPU)"
echo "3. Run with Docker command (CPU)"
echo "4. Exit"
echo ""
read -p "Select option (1-4): " option

case $option in
    1)
        if [ "$USE_COMPOSE" = true ]; then
            echo "🚀 Starting with Docker Compose..."
            if [ "$GPU_AVAILABLE" = false ]; then
                # Modify docker-compose.yml to remove GPU section
                sed -i.bak '/deploy:/,/capabilities: \[gpu\]/d' docker-compose.yml
            fi
            docker-compose up -d
            echo -e "${GREEN}✓ Application started with Docker Compose${NC}"
            echo ""
            echo "📊 View logs: docker-compose logs -f"
            echo "🛑 Stop: docker-compose down"
        else
            echo -e "${RED}❌ Docker Compose not available${NC}"
            exit 1
        fi
        ;;
    2)
        if [ "$GPU_AVAILABLE" = true ]; then
            echo "🚀 Starting with GPU support..."
            docker run -d \
                --name ai-image-generator \
                --gpus all \
                -p 8000:8000 \
                -v $(pwd)/models:/app/models \
                --restart unless-stopped \
                ai-image-generator
            echo -e "${GREEN}✓ Application started with GPU support${NC}"
        else
            echo -e "${RED}❌ No GPU available${NC}"
            exit 1
        fi
        ;;
    3)
        echo "🚀 Starting with CPU..."
        docker run -d \
            --name ai-image-generator \
            -p 8000:8000 \
            -v $(pwd)/models:/app/models \
            --restart unless-stopped \
            ai-image-generator
        echo -e "${GREEN}✓ Application started with CPU${NC}"
        ;;
    4)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid option${NC}"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo ""
echo "📱 Access the application at: http://localhost:8000"
echo ""
echo "⚠️  First run will download the model (~5GB)"
echo "    This may take 5-10 minutes depending on your connection"
echo ""
echo "📊 Monitor status:"
echo "   docker logs -f ai-image-generator"
echo ""
echo "🛑 Stop the application:"
echo "   docker stop ai-image-generator"
echo ""
echo "🔄 Restart the application:"
echo "   docker restart ai-image-generator"
echo ""
echo "🗑️  Remove the application:"
echo "   docker rm -f ai-image-generator"
echo ""
echo "=========================================="
