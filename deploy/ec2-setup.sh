#!/bin/bash
# =============================================================================
# GEO Content Platform - EC2 Setup Script
# =============================================================================
# Run this script on a fresh Amazon Linux 2023 EC2 instance to set up the
# GEO Content Platform backend.
#
# Usage: sudo bash ec2-setup.sh
# =============================================================================

set -e

echo "=============================================="
echo "GEO Content Platform - EC2 Setup"
echo "=============================================="

# Update system
echo "Updating system packages..."
dnf update -y

# Install required packages
echo "Installing required packages..."
dnf install -y \
    python3.11 \
    python3.11-pip \
    nginx \
    git \
    gcc \
    python3.11-devel

# Install uv package manager
echo "Installing uv package manager..."
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# Create application user
echo "Creating geo_content user..."
useradd -r -s /bin/false geo_content || true

# Create directories
echo "Creating application directories..."
mkdir -p /opt/geo_content
mkdir -p /var/lib/geo_content
mkdir -p /var/log/geo_content

# Set permissions
chown -R geo_content:geo_content /opt/geo_content
chown -R geo_content:geo_content /var/lib/geo_content
chown -R geo_content:geo_content /var/log/geo_content

# Install CloudWatch agent
echo "Installing CloudWatch agent..."
dnf install -y amazon-cloudwatch-agent || true

# Configure CloudWatch agent
cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json << 'EOF'
{
    "logs": {
        "logs_collected": {
            "files": {
                "collect_list": [
                    {
                        "file_path": "/var/log/geo_content/*.log",
                        "log_group_name": "geo-content-platform",
                        "log_stream_name": "{instance_id}/app",
                        "timezone": "UTC"
                    },
                    {
                        "file_path": "/var/log/nginx/access.log",
                        "log_group_name": "geo-content-platform",
                        "log_stream_name": "{instance_id}/nginx-access",
                        "timezone": "UTC"
                    },
                    {
                        "file_path": "/var/log/nginx/error.log",
                        "log_group_name": "geo-content-platform",
                        "log_stream_name": "{instance_id}/nginx-error",
                        "timezone": "UTC"
                    }
                ]
            }
        }
    }
}
EOF

# Start CloudWatch agent
systemctl enable amazon-cloudwatch-agent || true
systemctl start amazon-cloudwatch-agent || true

# Install certbot for SSL (optional)
echo "Installing certbot for SSL..."
dnf install -y certbot python3-certbot-nginx || true

echo "=============================================="
echo "EC2 Setup Complete!"
echo "=============================================="
echo ""
echo "Next steps:"
echo "1. Clone your repository to /opt/geo_content"
echo "2. Copy deploy/geo-content.service to /etc/systemd/system/"
echo "3. Copy deploy/nginx.conf to /etc/nginx/conf.d/geo-content.conf"
echo "4. Run: systemctl daemon-reload"
echo "5. Run: systemctl enable geo-content nginx"
echo "6. Run: systemctl start geo-content nginx"
echo ""
