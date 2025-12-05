#!/bin/bash
# =============================================================================
# GEO Content Platform - Deployment Script
# =============================================================================
# Run this script to deploy updates to the GEO Content Platform.
#
# Usage: sudo bash deploy.sh
# =============================================================================

set -e

APP_DIR="/opt/geo_content"
REPO_URL="https://github.com/your-org/geo-content-platform.git"  # Update this

echo "=============================================="
echo "GEO Content Platform - Deploying Updates"
echo "=============================================="

cd $APP_DIR

# Pull latest code (if using git)
if [ -d ".git" ]; then
    echo "Pulling latest code..."
    git pull origin main
fi

# Sync dependencies
echo "Installing dependencies with uv..."
/root/.local/bin/uv sync

# Install playwright browsers if needed
echo "Installing Playwright browsers..."
/root/.local/bin/uv run playwright install chromium || true

# Create log directory if it doesn't exist
mkdir -p /var/log/geo_content
chown -R geo_content:geo_content /var/log/geo_content

# Restart the service
echo "Restarting geo-content service..."
systemctl restart geo-content

# Wait for service to start
sleep 3

# Check health
echo "Checking service health..."
if curl -s http://localhost:8000/api/v1/health | grep -q "healthy"; then
    echo "✓ Service is healthy!"
else
    echo "✗ Service health check failed!"
    echo "Checking logs..."
    journalctl -u geo-content --no-pager -n 50
    exit 1
fi

echo "=============================================="
echo "Deployment Complete!"
echo "=============================================="
