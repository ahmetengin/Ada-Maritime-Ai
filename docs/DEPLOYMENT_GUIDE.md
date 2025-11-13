# Ada Maritime AI - Deployment Guide

Complete deployment guide for production environments.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Docker Deployment](#docker-deployment)
4. [Manual Deployment](#manual-deployment)
5. [Database Setup](#database-setup)
6. [Configuration](#configuration)
7. [SSL/TLS Setup](#ssltls-setup)
8. [Monitoring](#monitoring)
9. [Backup & Recovery](#backup--recovery)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Hardware Requirements

**Minimum (Development)**
- CPU: 2 cores
- RAM: 4 GB
- Storage: 20 GB
- Network: 10 Mbps

**Recommended (Production)**
- CPU: 4+ cores
- RAM: 16 GB
- Storage: 100 GB SSD
- Network: 100 Mbps
- Backup storage: 500 GB

**For VHF Monitoring (Additional)**
- RTL-SDR USB dongle (RTL-SDR Blog V3 or Airspy Mini)
- VHF antenna (marine band 156-162 MHz)
- USB 3.0 port

### Software Requirements

- Docker 24+ & Docker Compose 2.20+
- Python 3.11+
- Node.js 20+
- PostgreSQL 16+
- Redis 7+
- Nginx (for reverse proxy)

---

## Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/Ada-Maritime-Ai.git
cd Ada-Maritime-Ai
```

### 2. Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit configuration
nano .env
```

**Required Variables:**

```env
# CRITICAL - MUST CHANGE IN PRODUCTION
ANTHROPIC_API_KEY=your_production_api_key_here
JWT_SECRET_KEY=generate_random_secret_here_min_32_chars
POSTGRES_PASSWORD=strong_password_here

# Database
DATABASE_URL=postgresql://ada:your_password@postgres:5432/ada_ecosystem

# Email (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_USER=your_email@example.com
SMTP_PASSWORD=your_app_password

# Production settings
ENV=production
API_WORKERS=4
LOG_LEVEL=INFO
```

### 3. Generate Secrets

```bash
# Generate JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate database password
python -c "import secrets; print(secrets.token_urlsafe(24))"
```

---

## Docker Deployment

### Quick Start

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### Production Deployment

```bash
# Pull latest images
docker-compose pull

# Build with production settings
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Start in production mode
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Initialize database
docker-compose exec backend python -m backend.database.init_db

# Check health
curl http://localhost:8000/health
```

### Scale Services

```bash
# Scale backend API
docker-compose up -d --scale backend=4

# Scale frontend
docker-compose up -d --scale frontend=2
```

---

## Manual Deployment

### 1. Database Setup

```bash
# Install PostgreSQL
sudo apt install postgresql-16

# Create database and user
sudo -u postgres psql
CREATE DATABASE ada_ecosystem;
CREATE USER ada WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ada_ecosystem TO ada;
\q

# Initialize schema
cd backend
python -m database.init_db
```

### 2. Backend API

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Run migrations (if using Alembic)
alembic upgrade head

# Start API server
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3. Frontend Dashboard

```bash
# Install dependencies
cd frontend
npm install

# Build for production
npm run build

# Serve with nginx or static server
npm run preview
```

### 4. Process Manager (PM2)

```bash
# Install PM2
npm install -g pm2

# Backend
pm2 start "uvicorn api:app --host 0.0.0.0 --port 8000" --name ada-backend

# Frontend
pm2 start "npm run preview" --name ada-frontend

# Save PM2 configuration
pm2 save
pm2 startup
```

---

## Configuration

### Nginx Reverse Proxy

Create `/etc/nginx/sites-available/ada-maritime`:

```nginx
server {
    listen 80;
    server_name adamaritime.ai www.adamaritime.ai;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name adamaritime.ai www.adamaritime.ai;

    ssl_certificate /etc/letsencrypt/live/adamaritime.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/adamaritime.ai/privkey.pem;

    # API Backend
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

Enable and restart:

```bash
sudo ln -s /etc/nginx/sites-available/ada-maritime /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## SSL/TLS Setup

### Using Let's Encrypt (Certbot)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d adamaritime.ai -d www.adamaritime.ai

# Auto-renewal (cron)
sudo crontab -e
# Add: 0 0 * * * certbot renew --quiet
```

---

## Monitoring

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Database connection
curl http://localhost:8000/health/db

# Redis connection
curl http://localhost:8000/health/redis
```

### Logging

**Centralized Logging with ELK Stack:**

```yaml
# Add to docker-compose.yml
elasticsearch:
  image: elasticsearch:8.11
  ports: ["9200:9200"]
  environment:
    - discovery.type=single-node

kibana:
  image: kibana:8.11
  ports: ["5601:5601"]
  depends_on: [elasticsearch]

logstash:
  image: logstash:8.11
  volumes: ["./logstash.conf:/usr/share/logstash/pipeline/logstash.conf"]
  depends_on: [elasticsearch]
```

### Metrics (Prometheus + Grafana)

```yaml
prometheus:
  image: prom/prometheus
  ports: ["9090:9090"]
  volumes: ["./prometheus.yml:/etc/prometheus/prometheus.yml"]

grafana:
  image: grafana/grafana
  ports: ["3001:3000"]
  depends_on: [prometheus]
```

---

## Backup & Recovery

### Database Backup

```bash
# Automated daily backup
cat > /usr/local/bin/ada-backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/ada-maritime"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# PostgreSQL backup
pg_dump -U ada ada_ecosystem | gzip > $BACKUP_DIR/postgres_$DATE.sql.gz

# Redis backup
redis-cli SAVE
cp /var/lib/redis/dump.rdb $BACKUP_DIR/redis_$DATE.rdb

# Keep last 30 days
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
find $BACKUP_DIR -name "*.rdb" -mtime +30 -delete
EOF

chmod +x /usr/local/bin/ada-backup.sh

# Schedule with cron
echo "0 2 * * * /usr/local/bin/ada-backup.sh" | sudo crontab -
```

### Restore

```bash
# Restore PostgreSQL
gunzip < postgres_20250101.sql.gz | psql -U ada ada_ecosystem

# Restore Redis
redis-cli SHUTDOWN
cp redis_20250101.rdb /var/lib/redis/dump.rdb
redis-server
```

---

## Security Best Practices

### 1. Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 2. Rate Limiting

Add to Nginx:

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

location /api {
    limit_req zone=api_limit burst=20 nodelay;
    proxy_pass http://localhost:8000;
}
```

### 3. Database Security

```sql
-- Restrict database access
ALTER USER ada SET search_path TO public;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO ada;

-- Enable SSL
ALTER SYSTEM SET ssl = on;
```

---

## Troubleshooting

### Backend Not Starting

```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Missing ANTHROPIC_API_KEY
# 2. Database connection failed
# 3. Port 8000 already in use

# Check port
sudo lsof -i :8000
```

### Database Connection Error

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Test connection
docker-compose exec postgres psql -U ada -d ada_ecosystem -c "SELECT 1;"

# Check credentials in .env
```

### High Memory Usage

```bash
# Check resource usage
docker stats

# Adjust memory limits in docker-compose.yml
services:
  backend:
    mem_limit: 2g
    mem_reservation: 1g
```

### VHF SDR Issues

```bash
# Check RTL-SDR device
lsusb | grep RTL

# Test device
rtl_test

# Install drivers
sudo apt install rtl-sdr librtlsdr-dev
```

---

## Performance Tuning

### PostgreSQL

```sql
-- /etc/postgresql/16/main/postgresql.conf
max_connections = 100
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 10MB
min_wal_size = 1GB
max_wal_size = 4GB
```

### API Workers

```bash
# CPU cores * 2 + 1
WORKERS=$(($(nproc) * 2 + 1))
uvicorn api:app --workers $WORKERS
```

---

## Production Checklist

- [ ] Change all default passwords
- [ ] Set strong JWT_SECRET_KEY
- [ ] Configure SSL/TLS certificates
- [ ] Setup automated backups
- [ ] Enable monitoring and alerts
- [ ] Configure log rotation
- [ ] Setup firewall rules
- [ ] Test disaster recovery
- [ ] Document custom configuration
- [ ] Setup CI/CD pipeline
- [ ] Load testing completed
- [ ] Security audit passed

---

## Support

For deployment issues:
- Check logs: `docker-compose logs`
- Review documentation
- Contact support team

**Last Updated**: 2025-11-13
