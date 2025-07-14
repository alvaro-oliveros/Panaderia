#!/bin/bash

# Cleanup Script for Old SQLite Deployment
# Run this on your EC2 instance before deploying PostgreSQL version

echo "🧹 Cleaning up old SQLite deployment..."
echo "======================================"

# Stop and remove old containers
echo "🛑 Stopping old containers..."
docker stop bakery-app 2>/dev/null || echo "   No bakery-app container running"
docker rm bakery-app 2>/dev/null || echo "   No bakery-app container to remove"

# Stop any docker-compose services that might be running
echo "🛑 Stopping any docker-compose services..."
docker-compose down -v 2>/dev/null || echo "   No docker-compose services running"

# Remove old images
echo "🗑️  Removing old Docker images..."
docker rmi bakery-app 2>/dev/null || echo "   No bakery-app image to remove"
docker rmi panaderia-bakery-app 2>/dev/null || echo "   No panaderia-bakery-app image to remove"

# Clean up unused Docker resources
echo "🧽 Cleaning up unused Docker resources..."
docker system prune -af
docker volume prune -f

# Remove old SQLite database if it exists
echo "🗄️  Checking for old SQLite database..."
if [ -f "backend/panaderia.db" ]; then
    echo "   Found SQLite database, backing up..."
    cp backend/panaderia.db backup-sqlite-$(date +%Y%m%d-%H%M%S).db
    echo "   Backup created: backup-sqlite-$(date +%Y%m%d-%H%M%S).db"
    rm backend/panaderia.db
    echo "   Old SQLite database removed"
else
    echo "   No SQLite database found"
fi

# Remove old .env file
echo "⚙️  Removing old environment file..."
if [ -f ".env" ]; then
    cp .env .env.backup-$(date +%Y%m%d-%H%M%S)
    echo "   Backed up .env to .env.backup-$(date +%Y%m%d-%H%M%S)"
    rm .env
    echo "   Old .env removed"
else
    echo "   No .env file to remove"
fi

# Check for any running processes on ports 8000 and 3000
echo "🔍 Checking for processes on ports 8000 and 3000..."
PROC_8000=$(lsof -ti:8000 2>/dev/null || true)
PROC_3000=$(lsof -ti:3000 2>/dev/null || true)

if [ ! -z "$PROC_8000" ]; then
    echo "   Killing process on port 8000: $PROC_8000"
    kill -9 $PROC_8000 2>/dev/null || true
fi

if [ ! -z "$PROC_3000" ]; then
    echo "   Killing process on port 3000: $PROC_3000"
    kill -9 $PROC_3000 2>/dev/null || true
fi

# Final Docker cleanup
echo "🔄 Final Docker cleanup..."
docker container prune -f
docker image prune -af
docker network prune -f

echo ""
echo "✅ Cleanup completed successfully!"
echo "=================================="
echo "📊 Current Docker status:"
docker ps -a
echo ""
echo "💾 Available disk space:"
df -h /
echo ""
echo "🚀 Ready for PostgreSQL deployment!"
echo "   Run: ./deploy-ec2.sh"
echo "=================================="