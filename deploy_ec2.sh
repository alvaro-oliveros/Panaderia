#!/bin/bash

# Fresh EC2 Deployment Script
# This script deploys the panaderia application to a fresh EC2 instance

echo "🚀 Starting fresh deployment to EC2..."

# Configuration
EC2_HOST="ec2-18-221-210-76.us-east-2.compute.amazonaws.com"
EC2_USER="ubuntu"
KEY_PATH="/Users/alvaro/Desktop/Panaderia/Pan.pem"
REMOTE_DIR="/home/ubuntu/panaderia"

# Step 1: Clean up existing deployment
echo "🧹 Cleaning up existing deployment..."
ssh -i "$KEY_PATH" "$EC2_USER@$EC2_HOST" "
    sudo docker stop \$(sudo docker ps -q) 2>/dev/null || true
    sudo docker system prune -af
    sudo rm -rf $REMOTE_DIR
    mkdir -p $REMOTE_DIR
"

# Step 2: Copy application files
echo "📦 Copying application files..."
scp -i "$KEY_PATH" -r \
    ./backend \
    ./frontend \
    ./generate_business_data.py \
    ./test_humidity_data.py \
    ./.env.example \
    "$EC2_USER@$EC2_HOST:$REMOTE_DIR/"

# Step 3: Create optimized Docker files
echo "🐳 Creating Docker configuration..."
ssh -i "$KEY_PATH" "$EC2_USER@$EC2_HOST" "
    cd $REMOTE_DIR
    
    # Create requirements.txt
    cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
requests==2.31.0
python-multipart==0.0.6
EOF

    # Create simple Dockerfile
    cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create database with proper permissions
RUN mkdir -p /app/data && chmod 755 /app/data
RUN touch /app/panaderia.db && chmod 666 /app/panaderia.db

# Set environment
ENV DATABASE_URL=sqlite:///panaderia.db
ENV PYTHONPATH=/app

EXPOSE 8000 3000

# Start script
RUN echo '#!/bin/bash\ncd /app\npython -m http.server 3000 --directory frontend --bind 0.0.0.0 &\nuvicorn backend.app.main:app --host 0.0.0.0 --port 8000' > start.sh && chmod +x start.sh

CMD [\"./start.sh\"]
EOF

    # Create docker-compose.yml
    cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  panaderia:
    build: .
    ports:
      - \"8000:8000\"
      - \"3000:3000\"
    environment:
      - DATABASE_URL=sqlite:///panaderia.db
      - CORS_ORIGINS=http://panaderia-icc.duckdns.org,https://panaderia-icc.duckdns.org,http://18.221.210.76,http://localhost:3000
    volumes:
      - ./data:/app/data
    restart: unless-stopped
EOF
"

# Step 4: Build and start application
echo "🏗️ Building and starting application..."
ssh -i "$KEY_PATH" "$EC2_USER@$EC2_HOST" "
    cd $REMOTE_DIR
    sudo docker-compose up -d --build
"

# Step 5: Configure nginx
echo "🌐 Configuring nginx..."
ssh -i "$KEY_PATH" "$EC2_USER@$EC2_HOST" "
    sudo tee /etc/nginx/sites-available/panaderia > /dev/null << 'EOF'
server {
    listen 80;
    server_name panaderia-icc.duckdns.org 18.221.210.76;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Direct backend routes for ESP32
    location ~ ^/(sedes|productos|movimientos|usuarios|sensores|temperatura|humedad|analytics)/ {
        proxy_pass http://localhost:8000\$request_uri;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # API docs
    location /docs {
        proxy_pass http://localhost:8000/docs;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

    sudo ln -sf /etc/nginx/sites-available/panaderia /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl restart nginx
"

# Step 6: Wait for application to start
echo "⏳ Waiting for application to start..."
sleep 30

# Step 7: Test deployment
echo "🧪 Testing deployment..."
ssh -i "$KEY_PATH" "$EC2_USER@$EC2_HOST" "
    echo 'Testing backend API...'
    curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/docs
    echo
    echo 'Testing frontend...'
    curl -s -o /dev/null -w '%{http_code}' http://localhost:3000
    echo
    echo 'Docker containers:'
    sudo docker ps
"

echo "✅ Deployment complete!"
echo "🌐 Frontend: http://panaderia-icc.duckdns.org"
echo "🔧 Backend API: http://panaderia-icc.duckdns.org/docs"
echo "📊 ESP32 can post to: http://panaderia-icc.duckdns.org/temperatura/ and /humedad/"