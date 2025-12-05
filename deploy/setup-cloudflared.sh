#!/bin/bash
# Cloudflare Tunnel Setup Script for EC2
# Run this script on your EC2 instance (18.138.26.110)

set -e  # Exit on error

echo "========================================"
echo "Cloudflare Tunnel Setup for GEO Content"
echo "========================================"
echo ""

# Step 1: Install cloudflared
echo "Step 1/7: Installing cloudflared..."
cd /tmp
if [ ! -f cloudflared-linux-amd64.deb ]; then
    wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
fi
sudo dpkg -i cloudflared-linux-amd64.deb

# Verify installation
echo "Cloudflared version:"
cloudflared --version
echo ""

# Step 2: Authenticate
echo "Step 2/7: Authenticate with Cloudflare"
echo "This will open a browser window. Please complete authentication."
echo "Press Enter to continue..."
read

cloudflared tunnel login

if [ ! -f ~/.cloudflared/cert.pem ]; then
    echo "ERROR: Authentication failed. cert.pem not found."
    exit 1
fi

echo "✓ Authentication successful!"
echo ""

# Step 3: Create tunnel
echo "Step 3/7: Creating tunnel 'geo-content-backend'..."
cloudflared tunnel create geo-content-backend

# Find the tunnel ID and credentials file
TUNNEL_ID=$(cloudflared tunnel list | grep geo-content-backend | awk '{print $1}')
CREDS_FILE="$HOME/.cloudflared/${TUNNEL_ID}.json"

if [ -z "$TUNNEL_ID" ]; then
    echo "ERROR: Failed to create tunnel"
    exit 1
fi

echo "✓ Tunnel created with ID: $TUNNEL_ID"
echo "✓ Credentials file: $CREDS_FILE"
echo ""

# Step 4: Create config file
echo "Step 4/7: Creating tunnel configuration..."
sudo mkdir -p /etc/cloudflared

sudo tee /etc/cloudflared/config.yml > /dev/null <<EOF
tunnel: $TUNNEL_ID
credentials-file: $CREDS_FILE

ingress:
  - hostname: api.geoaction.tocanan.ai
    service: http://localhost:80
  - service: http_status:404
EOF

echo "✓ Configuration created at /etc/cloudflared/config.yml"
echo ""

# Step 5: Route DNS
echo "Step 5/7: Creating DNS record for api.geoaction.tocanan.ai..."
cloudflared tunnel route dns geo-content-backend api.geoaction.tocanan.ai

echo "✓ DNS record created"
echo ""

# Step 6: Install and start service
echo "Step 6/7: Installing and starting cloudflared service..."
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared

# Wait for service to start
sleep 3

echo "✓ Service installed and started"
echo ""

# Step 7: Verify
echo "Step 7/7: Verifying tunnel..."
sudo systemctl status cloudflared --no-pager

echo ""
echo "Testing tunnel connection..."
curl -s -H "Host: api.geoaction.tocanan.ai" http://localhost:80/api/v1/health || echo "Note: Test failed, but tunnel may still be working"

echo ""
echo "========================================"
echo "✓ Cloudflare Tunnel Setup Complete!"
echo "========================================"
echo ""
echo "Tunnel ID: $TUNNEL_ID"
echo "DNS Record: api.geoaction.tocanan.ai -> ${TUNNEL_ID}.cfargotunnel.com"
echo ""
echo "Next steps:"
echo "1. Run: sudo nano /etc/systemd/system/geo-content.service"
echo "2. Update CORS_ORIGINS to: https://geoaction.tocanan.ai,http://localhost:3000"
echo "3. Run: sudo systemctl daemon-reload"
echo "4. Run: sudo systemctl restart geo-content"
echo "5. Follow CLOUDFLARE_SETUP.md for Cloudflare Zero Trust configuration"
echo ""
