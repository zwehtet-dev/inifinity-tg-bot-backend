#!/bin/bash
set -e

echo "🛑 Stopping containers..."
docker compose down

echo "🔨 Building image..."
docker compose build

echo "🚀 Starting containers..."
docker compose up -d

echo "⏳ Waiting for backend to be ready..."
sleep 5

echo "📋 Checking logs..."
docker compose logs --tail=50 backend

echo ""
echo "✅ Done! Check status with: docker compose ps"
echo "📋 View logs with: docker compose logs -f backend"
