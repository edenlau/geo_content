#!/bin/bash
# Update Backend CORS Configuration
# Run this script on EC2 after installing cloudflared

set -e

echo "========================================"
echo "Updating Backend CORS Configuration"
echo "========================================"
echo ""

# Backup current service file
echo "Creating backup of geo-content.service..."
sudo cp /etc/systemd/system/geo-content.service /etc/systemd/system/geo-content.service.backup.$(date +%Y%m%d_%H%M%S)

# Check if CORS_ORIGINS exists
if sudo grep -q "Environment=CORS_ORIGINS=" /etc/systemd/system/geo-content.service; then
    echo "Updating existing CORS_ORIGINS..."
    sudo sed -i 's|Environment=CORS_ORIGINS=.*|Environment=CORS_ORIGINS=https://geoaction.tocanan.ai,http://localhost:3000|' /etc/systemd/system/geo-content.service
else
    echo "Adding CORS_ORIGINS..."
    # Add after other Environment= lines
    sudo sed -i '/Environment=S3_BUCKET_UPLOADS=/a Environment=CORS_ORIGINS=https://geoaction.tocanan.ai,http://localhost:3000' /etc/systemd/system/geo-content.service
fi

echo "✓ Updated CORS configuration"
echo ""

# Show the updated line
echo "Updated configuration:"
sudo grep "Environment=CORS_ORIGINS=" /etc/systemd/system/geo-content.service

echo ""
echo "Reloading systemd and restarting service..."
sudo systemctl daemon-reload
sudo systemctl restart geo-content

# Wait for service to start
sleep 2

echo ""
echo "Checking service status..."
sudo systemctl status geo-content --no-pager || true

echo ""
echo "Testing backend health..."
curl -s http://localhost:80/api/v1/health | python3 -m json.tool || echo "Health check failed"

echo ""
echo "========================================"
echo "✓ Backend CORS Update Complete!"
echo "========================================"
echo ""
echo "Service is now configured to accept requests from:"
echo "  - https://geoaction.tocanan.ai"
echo "  - http://localhost:3000"
echo ""
