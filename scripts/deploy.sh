#!/bin/bash

# Resume Parser Production Deployment Script
# This script handles the deployment of the Resume Parser application

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env"
BACKUP_DIR="backups"
LOG_FILE="deploy.log"

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root for security reasons."
    fi
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed. Please install Docker Compose first."
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running. Please start Docker first."
    fi
    
    # Check if .env file exists
    if [[ ! -f "$ENV_FILE" ]]; then
        error "Environment file $ENV_FILE not found. Please create it from .env.example"
    fi
    
    log "Prerequisites check passed ✓"
}

# Backup database
backup_database() {
    log "Creating database backup..."
    
    # Create backup directory if it doesn't exist
    mkdir -p "$BACKUP_DIR"
    
    # Generate backup filename with timestamp
    BACKUP_FILE="${BACKUP_DIR}/database_backup_$(date +%Y%m%d_%H%M%S).sql"
    
    # Create database backup
    if docker-compose -f "$COMPOSE_FILE" ps postgres | grep -q "Up"; then
        docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_dump -U postgres resume_parser > "$BACKUP_FILE"
        log "Database backup created: $BACKUP_FILE ✓"
    else
        warn "PostgreSQL container not running, skipping database backup"
    fi
}

# Pull latest images
pull_images() {
    log "Pulling latest Docker images..."
    docker-compose -f "$COMPOSE_FILE" pull
    log "Docker images pulled ✓"
}

# Build custom images
build_images() {
    log "Building custom Docker images..."
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    log "Docker images built ✓"
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    docker-compose -f "$COMPOSE_FILE" exec -T backend alembic upgrade head
    log "Database migrations completed ✓"
}

# Health check
health_check() {
    log "Performing health checks..."
    
    # Wait for services to be ready
    sleep 30
    
    # Check backend health
    if curl -f http://localhost:8000/health &> /dev/null; then
        log "Backend health check passed ✓"
    else
        error "Backend health check failed"
    fi
    
    # Check frontend accessibility
    if curl -f http://localhost:3000 &> /dev/null; then
        log "Frontend health check passed ✓"
    else
        error "Frontend health check failed"
    fi
    
    log "All health checks passed ✓"
}

# Deploy application
deploy() {
    log "Starting deployment..."
    
    # Pull latest changes
    log "Pulling latest code changes..."
    git pull origin main
    
    # Stop existing containers
    log "Stopping existing containers..."
    docker-compose -f "$COMPOSE_FILE" down
    
    # Remove old volumes (optional - commented out for safety)
    # log "Removing old volumes..."
    # docker-compose -f "$COMPOSE_FILE" down -v
    
    # Build and start containers
    log "Building and starting containers..."
    docker-compose -f "$COMPOSE_FILE" up -d --build
    
    # Wait for services to be ready
    log "Waiting for services to be ready..."
    sleep 60
    
    # Run migrations
    run_migrations
    
    # Health check
    health_check
    
    log "Deployment completed successfully ✓"
}

# Rollback to previous version
rollback() {
    log "Rolling back to previous version..."
    
    # Stop current containers
    docker-compose -f "$COMPOSE_FILE" down
    
    # Restore from backup
    if [[ -n "$1" ]]; then
        BACKUP_FILE="$1"
        if [[ -f "$BACKUP_FILE" ]]; then
            log "Restoring database from backup: $BACKUP_FILE"
            docker-compose -f "$COMPOSE_FILE" up -d postgres
            sleep 30
            docker-compose -f "$COMPOSE_FILE" exec -T postgres psql -U postgres -d resume_parser < "$BACKUP_FILE"
            log "Database restored ✓"
        else
            error "Backup file not found: $BACKUP_FILE"
        fi
    fi
    
    # Start containers with previous version
    docker-compose -f "$COMPOSE_FILE" up -d
    
    log "Rollback completed ✓"
}

# Setup SSL certificates
setup_ssl() {
    log "Setting up SSL certificates..."
    
    # Create directories
    mkdir -p certbot/conf certbot/www
    
    # Generate certificates
    docker-compose -f "$COMPOSE_FILE" run --rm certbot
    
    # Reload nginx
    docker-compose -f "$COMPOSE_FILE" exec nginx nginx -s reload
    
    log "SSL certificates setup completed ✓"
}

# Monitor services
monitor() {
    log "Monitoring services..."
    
    # Show container status
    docker-compose -f "$COMPOSE_FILE" ps
    
    # Show logs
    docker-compose -f "$COMPOSE_FILE" logs --tail=50 -f
}

# Cleanup old images and volumes
cleanup() {
    log "Cleaning up old Docker images and volumes..."
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes
    docker volume prune -f
    
    # Remove unused networks
    docker network prune -f
    
    log "Cleanup completed ✓"
}

# Show usage
usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  deploy        Deploy the application"
    echo "  rollback      Rollback to previous version"
    echo "  backup        Create database backup"
    echo "  ssl           Setup SSL certificates"
    echo "  monitor       Monitor services"
    echo "  cleanup       Cleanup old images and volumes"
    echo "  health        Run health checks"
    echo "  logs          Show application logs"
    echo "  help          Show this help message"
}

# Main script
main() {
    case "${1:-deploy}" in
        deploy)
            check_root
            check_prerequisites
            backup_database
            deploy
            ;;
        rollback)
            check_root
            rollback "$2"
            ;;
        backup)
            backup_database
            ;;
        ssl)
            setup_ssl
            ;;
        monitor)
            monitor
            ;;
        cleanup)
            cleanup
            ;;
        health)
            health_check
            ;;
        logs)
            docker-compose -f "$COMPOSE_FILE" logs -f
            ;;
        help)
            usage
            ;;
        *)
            error "Unknown command: $1"
            usage
            ;;
    esac
}

# Run main function
main "$@"
