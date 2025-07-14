# AWS EC2 PostgreSQL Deployment Guide

## Prerequisites

1. **EC2 Instance Requirements:**
   - Ubuntu 22.04 LTS or newer
   - t3.medium or larger (2GB+ RAM for PostgreSQL)
   - 20GB+ storage
   - Security groups allowing ports: 22 (SSH), 80 (HTTP), 443 (HTTPS), 8000 (API), 3000 (Frontend)

2. **Required Software on EC2:**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker ubuntu
   
   # Install Docker Compose
   sudo apt install docker-compose-plugin -y
   
   # Install Git and curl
   sudo apt install git curl -y
   ```

## Environment Variables Setup

Set these environment variables on your EC2 instance:

```bash
# PostgreSQL Configuration
export POSTGRES_PASSWORD="your_secure_password_here"

# API Keys (optional)
export OPENAI_API_KEY="your_openai_key"
export CLAUDE_API_KEY="your_claude_key"

# Add to ~/.bashrc for persistence
echo 'export POSTGRES_PASSWORD="your_secure_password_here"' >> ~/.bashrc
echo 'export OPENAI_API_KEY="your_openai_key"' >> ~/.bashrc
echo 'export CLAUDE_API_KEY="your_claude_key"' >> ~/.bashrc
source ~/.bashrc
```

## Deployment Steps

1. **Clone Repository:**
   ```bash
   git clone https://github.com/alvaro-oliveros/Panaderia.git
   cd Panaderia
   ```

2. **Run Deployment Script:**
   ```bash
   chmod +x deploy-ec2.sh
   ./deploy-ec2.sh your-domain-or-ip
   ```

   Or with automatic IP detection:
   ```bash
   ./deploy-ec2.sh
   ```

## Security Configuration

1. **Update Security Groups:**
   - Port 5432: Remove from public access (PostgreSQL should only be accessible from within Docker network)
   - Port 8000: Backend API
   - Port 3000: Frontend
   - Port 22: SSH access

2. **SSL/HTTPS Setup:**
   - The deployment uses DuckDNS (panaderia-icc.duckdns.org)
   - Update your DuckDNS token if needed
   - Consider adding Let's Encrypt SSL certificates

## Database Management

- **Backup Database:**
  ```bash
  docker-compose exec postgres pg_dump -U bakery_admin panaderia > backup.sql
  ```

- **Restore Database:**
  ```bash
  docker-compose exec -T postgres psql -U bakery_admin panaderia < backup.sql
  ```

- **View Database:**
  ```bash
  docker-compose exec postgres psql -U bakery_admin panaderia
  ```

## Monitoring Commands

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs bakery-app
docker-compose logs postgres

# Restart services
docker-compose restart

# Update deployment
git pull origin main
docker-compose up --build -d
```

## Troubleshooting

1. **PostgreSQL Connection Issues:**
   - Check if container is running: `docker-compose ps`
   - View PostgreSQL logs: `docker-compose logs postgres`
   - Verify network connectivity: `docker network ls`

2. **ENUM Errors:**
   - Clear volumes and rebuild: `docker-compose down -v && docker-compose up --build -d`
   - Check model definitions in `backend/app/models.py`

3. **Permission Issues:**
   - Ensure user is in docker group: `groups $USER`
   - Fix file permissions: `sudo chown -R $USER:$USER .`