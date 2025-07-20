# Resume Parser - Deployment Guide

This document provides comprehensive instructions for deploying the Resume Parser application in production environments.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Production Deployment](#production-deployment)
4. [SSL Configuration](#ssl-configuration)
5. [Monitoring and Logging](#monitoring-and-logging)
6. [Backup and Recovery](#backup-and-recovery)
7. [Troubleshooting](#troubleshooting)
8. [Maintenance](#maintenance)

## 🔧 Prerequisites

### System Requirements

- **Operating System**: Ubuntu 20.04 LTS or CentOS 8+
- **Memory**: Minimum 8GB RAM (16GB recommended)
- **Storage**: Minimum 50GB available space
- **CPU**: 4+ cores recommended
- **Network**: Stable internet connection

### Software Requirements

- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+
- **Git**: Latest version
- **Curl**: For health checks
- **Nginx**: For reverse proxy (optional if using containerized version)

### Installation Commands

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.0.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
sudo apt-get update
sudo apt-get install git curl -y
```

## 🌍 Environment Setup

### 1. Clone Repository

```bash
git clone [<repository-url>](https://github.com/imadnan4/Hirify)
cd Hirify
```

### 2. Environment Configuration

Create production environment file:

```bash
cp .env.example .env
```

Edit `.env` with your production values:

```bash
# Database Configuration
DATABASE_NAME=resume_parser_prod
DATABASE_USER=postgres
DATABASE_PASSWORD=your_secure_password
DATABASE_HOST=postgres
DATABASE_PORT=5432

# Redis Configuration
REDIS_PASSWORD=your_redis_password
REDIS_HOST=redis
REDIS_PORT=6379

# Application Configuration
SECRET_KEY=your_super_secret_key_here
ENVIRONMENT=production
DEBUG=false

# CORS Configuration
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# SSL Configuration
DOMAIN=yourdomain.com
SSL_EMAIL=admin@yourdomain.com

# Security
JWT_SECRET_KEY=your_jwt_secret_key
ENCRYPTION_KEY=your_encryption_key

# Performance
MAX_WORKERS=4
CELERY_CONCURRENCY=4
MAX_FILE_SIZE=104857600  # 100MB

# Monitoring
GRAFANA_PASSWORD=your_grafana_password
PROMETHEUS_RETENTION=15d

```

### 3. Directory Structure

Create necessary directories:

```bash
mkdir -p backups logs uploads models
mkdir -p certbot/conf certbot/www
mkdir -p monitoring/prometheus monitoring/grafana/provisioning
mkdir -p nginx/conf.d
```

## 🚀 Production Deployment

### 1. Automatic Deployment

Use the provided deployment script:

```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh deploy
```

### 2. Manual Deployment

If you prefer manual deployment:

```bash
# Pull latest code
git pull origin main

# Create database backup (if updating)
./scripts/deploy.sh backup

# Build and start services
docker-compose -f docker-compose.prod.yml up -d --build

# Wait for services to start
sleep 60

# Run database migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Check health
curl -f http://localhost:8000/health
```

### 3. Service Verification

Check all services are running:

```bash
docker-compose -f docker-compose.prod.yml ps
```

Expected output:
```
NAME                           SERVICE         STATUS    PORTS
hirify-backend          backend         running   0.0.0.0:8000->8000/tcp
hirify-celery-worker    celery-worker   running   
hirify-frontend         frontend        running   0.0.0.0:3000->3000/tcp
hirify-nginx            nginx           running   0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
hirify-postgres         postgres        running   5432/tcp
hirify-redis            redis           running   6379/tcp
```

## 🔐 SSL Configuration

### 1. Let's Encrypt SSL

Setup automatic SSL certificates:

```bash
# Configure domain in .env file
echo "DOMAIN=yourdomain.com" >> .env
echo "SSL_EMAIL=admin@yourdomain.com" >> .env

# Generate certificates
./scripts/deploy.sh ssl
```

### 2. Manual SSL Configuration

If using custom certificates:

```bash
# Copy certificates to certbot directory
cp your_certificate.crt certbot/conf/live/yourdomain.com/fullchain.pem
cp your_private_key.key certbot/conf/live/yourdomain.com/privkey.pem

# Reload nginx
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

### 3. SSL Renewal

Setup automatic renewal:

```bash
# Add to crontab
echo "0 3 * * * /path/to/project/scripts/deploy.sh ssl" | crontab -
```

## 📊 Monitoring and Logging

### 1. Access Monitoring Services

- **Grafana**: http://yourdomain.com:3000
- **Prometheus**: http://yourdomain.com:9090
- **Kibana**: http://yourdomain.com:5601

### 2. Default Credentials

- **Grafana**: admin / (value of GRAFANA_PASSWORD)
- **Prometheus**: No authentication required
- **Kibana**: No authentication required

### 3. Log Locations

```bash
# Application logs
ls -la backend/logs/

# Container logs
docker-compose -f docker-compose.prod.yml logs [service_name]

# Nginx logs
docker-compose -f docker-compose.prod.yml exec nginx ls -la /var/log/nginx/
```

### 4. Performance Monitoring

Key metrics to monitor:
- CPU usage
- Memory usage
- Database connections
- API response times
- Error rates
- File upload success rates

## 💾 Backup and Recovery

### 1. Database Backup

Automated backups:

```bash
# Manual backup
./scripts/deploy.sh backup

# Automated backup (add to crontab)
echo "0 2 * * * /path/to/project/scripts/deploy.sh backup" | crontab -
```

### 2. File Backup

```bash
# Backup uploaded files
tar -czf backups/uploads_$(date +%Y%m%d_%H%M%S).tar.gz backend/uploads/

# Backup application data
tar -czf backups/app_data_$(date +%Y%m%d_%H%M%S).tar.gz backend/logs/ backend/models/
```

### 3. Recovery Process

```bash
# Stop services
docker-compose -f docker-compose.prod.yml down

# Restore database
docker-compose -f docker-compose.prod.yml up -d postgres
sleep 30
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U postgres -d resume_parser < backups/database_backup_YYYYMMDD_HHMMSS.sql

# Restore files
tar -xzf backups/uploads_YYYYMMDD_HHMMSS.tar.gz

# Start services
docker-compose -f docker-compose.prod.yml up -d
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Services Not Starting

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs

# Check specific service
docker-compose -f docker-compose.prod.yml logs backend

# Check system resources
docker stats
```

#### 2. Database Connection Issues

```bash
# Check PostgreSQL status
docker-compose -f docker-compose.prod.yml exec postgres pg_isready -U postgres

# Check database logs
docker-compose -f docker-compose.prod.yml logs postgres

# Test connection
docker-compose -f docker-compose.prod.yml exec backend python -c "from app.core.database import engine; print(engine.execute('SELECT 1').scalar())"
```

#### 3. SSL Certificate Issues

```bash
# Check certificate status
docker-compose -f docker-compose.prod.yml exec nginx ls -la /etc/letsencrypt/live/yourdomain.com/

# Test SSL
curl -I https://yourdomain.com

# Regenerate certificates
./scripts/deploy.sh ssl
```

#### 4. High Memory Usage

```bash
# Check memory usage
docker stats

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Scale down workers if needed
docker-compose -f docker-compose.prod.yml up -d --scale celery-worker=2
```

### Health Checks

```bash
# Backend health
curl -f http://localhost:8000/health

# Frontend health  
curl -f http://localhost:3000

# Database health
docker-compose -f docker-compose.prod.yml exec postgres pg_isready -U postgres

# Redis health
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping
```

## 🛠️ Maintenance

### Regular Tasks

#### 1. System Updates

```bash
# Update system packages
sudo apt-get update && sudo apt-get upgrade -y

# Update Docker images
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Clean up old images
./scripts/deploy.sh cleanup
```

#### 2. Database Maintenance

```bash
# Analyze database performance
docker-compose -f docker-compose.prod.yml exec postgres psql -U postgres -d resume_parser -c "ANALYZE;"

# Vacuum database
docker-compose -f docker-compose.prod.yml exec postgres psql -U postgres -d resume_parser -c "VACUUM;"

# Check database size
docker-compose -f docker-compose.prod.yml exec postgres psql -U postgres -d resume_parser -c "SELECT pg_size_pretty(pg_database_size('resume_parser'));"
```

#### 3. Log Rotation

```bash
# Setup logrotate
sudo cat > /etc/logrotate.d/hirify << EOF
/path/to/project/backend/logs/*.log {
    daily
    rotate 30
    compress
    missingok
    notifempty
    create 644 root root
}
EOF
```

### Security Updates

#### 1. Container Security

```bash
# Scan for vulnerabilities
docker scan hirify_backend

# Update base images
docker-compose -f docker-compose.prod.yml build --no-cache --pull
```

#### 2. SSL Certificate Renewal

```bash
# Check certificate expiration
openssl x509 -in certbot/conf/live/yourdomain.com/fullchain.pem -noout -dates

# Force renewal
docker-compose -f docker-compose.prod.yml run --rm certbot renew --force-renewal
```

### Performance Optimization

#### 1. Database Optimization

```bash
# Check slow queries
docker-compose -f docker-compose.prod.yml exec postgres psql -U postgres -d resume_parser -c "SELECT query, mean_time, calls FROM pg_stat_statements WHERE mean_time > 1000 ORDER BY mean_time DESC LIMIT 10;"

# Rebuild indexes
docker-compose -f docker-compose.prod.yml exec postgres psql -U postgres -d resume_parser -c "REINDEX DATABASE resume_parser;"
```

#### 2. Application Optimization

```bash
# Monitor application performance
./scripts/deploy.sh monitor

# Check resource usage
docker stats

# Scale services if needed
docker-compose -f docker-compose.prod.yml up -d --scale celery-worker=6
```

## 📞 Support

For deployment issues:

1. Check this documentation
2. Review application logs
3. Check system resources
4. Consult monitoring dashboards
5. Create an issue in the repository

## 📝 Notes

- Always backup before making changes
- Test deployments in staging environment first
- Monitor resource usage after deployment
- Keep security patches up to date
- Review logs regularly for issues
