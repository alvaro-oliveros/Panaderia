#\!/bin/bash

# EC2 Deployment Script for Bakery Management System (SQLite)
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
CORS_ORIGINS=https://panaderia-icc.duckdns.org,http://${EC2_IP}:3000,http://localhost:3000
OPENAI_API_KEY=\${OPENAI_API_KEY:-""}
CLAUDE_API_KEY=\${CLAUDE_API_KEY:-""}
