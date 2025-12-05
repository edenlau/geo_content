#!/bin/bash
# =============================================================================
# GEO Content Platform - Frontend Deployment Script
# =============================================================================
# Run this script from the project root to build and deploy the frontend to S3.
#
# Usage: bash deploy/deploy-frontend.sh
# =============================================================================

set -e

# Configuration
AWS_PROFILE="${AWS_PROFILE:-eden.lau.dev}"
AWS_REGION="ap-southeast-1"
S3_BUCKET="geo-content-frontend-053955129008"
FRONTEND_DIR="frontend"

echo "=============================================="
echo "GEO Content Platform - Frontend Deployment"
echo "=============================================="

# Check if we're in the right directory
if [ ! -d "$FRONTEND_DIR" ]; then
    echo "Error: frontend directory not found. Run from project root."
    exit 1
fi

cd $FRONTEND_DIR

# Install dependencies
echo "Installing dependencies..."
npm install

# Build for production
echo "Building frontend..."
npm run build

# Upload to S3
echo "Uploading to S3..."
aws s3 sync dist/ s3://${S3_BUCKET}/ \
    --profile ${AWS_PROFILE} \
    --region ${AWS_REGION} \
    --delete \
    --cache-control "max-age=31536000" \
    --exclude "index.html"

# Upload index.html with no-cache
aws s3 cp dist/index.html s3://${S3_BUCKET}/index.html \
    --profile ${AWS_PROFILE} \
    --region ${AWS_REGION} \
    --cache-control "no-cache, no-store, must-revalidate"

echo "=============================================="
echo "Frontend Deployment Complete!"
echo "=============================================="
echo ""
echo "Frontend URL: http://${S3_BUCKET}.s3-website-${AWS_REGION}.amazonaws.com"
echo ""
