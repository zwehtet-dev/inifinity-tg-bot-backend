#!/bin/bash
# Simple deployment script for Flask Backend

set -e

echo "🚀 Flask Backend - Deployment Script"
echo "====================================="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Creating from .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  Please edit .env with your configuration:"
    echo "  nano .env"
    echo ""
    read -p "Press Enter after editing .env, or Ctrl+C to cancel..."
fi

echo "✓ Found .env file"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed!"
    echo ""
    echo "Install Docker:"
    echo "  curl -fsSL https://get.docker.com -o get-docker.sh"
    echo "  sudo sh get-docker.sh"
    echo ""
    exit 1
fi

echo "✓ Docker is installed"

# Stop existing containers
echo ""
echo "🛑 Stopping existing containers..."
docker-compose down 2>/dev/null || echo "  No existing containers to stop"

# Build image
echo ""
echo "🔨 Building Docker image..."
docker-compose build

# Start containers
echo ""
echo "🚀 Starting containers..."
docker-compose up -d

# Wait for health check
echo ""
echo "⏳ Waiting for health check..."
sleep 10

# Check if container is running
if docker ps | grep -q "telegram-bot-backend"; then
    echo "✓ Container is running"
    
    # Check health
    echo ""
    echo "🏥 Checking health endpoint..."
    if curl -f http://localhost:5000/ 2>/dev/null; then
        echo ""
        echo "✅ Deployment successful!"
        echo ""
        echo "Backend URL: http://localhost:5000"
        echo "Container: telegram-bot-backend"
        echo ""
        echo "View logs:"
        echo "  docker-compose logs -f"
        echo ""
        echo "Check status:"
        echo "  docker-compose ps"
        echo ""
    else
        echo ""
        echo "⚠️  Container is running but health check failed"
        echo "Check logs:"
        echo "  docker-compose logs"
    fi
else
    echo "❌ Container failed to start"
    echo ""
    echo "Check logs:"
    echo "  docker-compose logs"
    exit 1
fi
