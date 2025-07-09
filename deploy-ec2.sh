#!/bin/bash

# EC2 Deployment Script for Bakery Management System
# Usage: ./deploy-ec2.sh [ec2-public-ip]

set -e

EC2_IP=${1:-"your-ec2-public-ip"}

echo "🚀 Deploying Bakery Management System to EC2..."
echo "================================================"

# Get EC2 public IP if not provided
if [ "$EC2_IP" = "your-ec2-public-ip" ]; then
    echo "📍 Getting EC2 public IP..."
    EC2_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "localhost")
fi

echo "🔧 Using EC2 IP: $EC2_IP"

# Create production environment file
echo "⚙️  Creating production environment..."
cat > .env << EOF
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite:///./panaderias.db
CORS_ORIGINS=http://${EC2_IP}:3000,http://localhost:3000
EOF

# Build Docker image
echo "🏗️  Building Docker image..."
docker build -t bakery-app .

# Stop existing container if running
echo "🛑 Stopping existing container..."
docker stop bakery-app 2>/dev/null || true
docker rm bakery-app 2>/dev/null || true

# Run new container
echo "🚀 Starting new container..."
docker run -d \
    --name bakery-app \
    --restart unless-stopped \
    -p 8000:8000 \
    -p 3000:3000 \
    -v bakery_data:/app/backend \
    --env-file .env \
    bakery-app

# Wait for container to start
echo "⏳ Waiting for container to start..."
sleep 10

# Health check
echo "🏥 Performing health check..."
if curl -f http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ Container is healthy!"
else
    echo "❌ Container health check failed!"
    docker logs bakery-app
    exit 1
fi

echo ""
echo "🎉 Deployment completed successfully!"
echo "================================================"
echo "🌐 Frontend: http://${EC2_IP}:3000/login.html"
echo "🔧 Backend API: http://${EC2_IP}:8000"
echo "📚 API Docs: http://${EC2_IP}:8000/docs"
echo "🏥 Health Check: http://${EC2_IP}:8000/health"
echo ""
echo "👥 Login credentials:"
echo "   Admin: admin / admin123"
echo "   User: user2 / user2"
echo "================================================"