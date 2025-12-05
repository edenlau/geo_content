# Cloudflare Zero Trust Deployment Guide

This guide walks you through deploying the GEO Content Platform using Cloudflare Zero Trust with authentication.

## Architecture Overview

```
Frontend: https://geoaction.tocanan.ai → S3 (via Cloudflare Proxy)
Backend:  https://api.geoaction.tocanan.ai → EC2 (via Cloudflare Tunnel)
```

## Prerequisites

- ✅ AWS credentials configured (eden.lau.dev profile)
- ✅ EC2 instance running (18.138.26.110)
- ✅ Cloudflare account with tocanan.ai domain
- ✅ SSH access to EC2 instance

---

## Part 1: Install Cloudflare Tunnel on EC2

### Step 1.1: SSH into EC2

```bash
ssh -i /Users/edenlau/Documents/pem_files/harbour-city-data-processing.pem ec2-user@18.138.26.110
```

### Step 1.2: Install cloudflared

```bash
# Download cloudflared
cd /tmp
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb

# Install
sudo dpkg -i cloudflared-linux-amd64.deb

# Verify installation
cloudflared --version
```

**Expected output:** `cloudflared version 2024.x.x`

### Step 1.3: Authenticate cloudflared

```bash
# This will open a browser window for authentication
cloudflared tunnel login
```

**What happens:**
1. Browser opens to Cloudflare authentication page
2. Select your Cloudflare account
3. Choose `tocanan.ai` domain
4. Authorize cloudflared

**Result:** Creates certificate file at `/home/ec2-user/.cloudflared/cert.pem`

### Step 1.4: Create the Tunnel

```bash
# Create a named tunnel
cloudflared tunnel create geo-content-backend
```

**Expected output:**
```
Tunnel credentials written to /home/ec2-user/.cloudflared/<TUNNEL-ID>.json
Created tunnel geo-content-backend with id <TUNNEL-ID>
```

**IMPORTANT:** Copy the `<TUNNEL-ID>` - you'll need it in the next step!

### Step 1.5: Configure the Tunnel

Create the tunnel configuration file:

```bash
# Create config directory
sudo mkdir -p /etc/cloudflared

# Create config file (use your tunnel ID from previous step)
sudo tee /etc/cloudflared/config.yml > /dev/null <<EOF
tunnel: <TUNNEL-ID>
credentials-file: /home/ec2-user/.cloudflared/<TUNNEL-ID>.json

ingress:
  - hostname: api.geoaction.tocanan.ai
    service: http://localhost:80
  - service: http_status:404
EOF
```

**Replace `<TUNNEL-ID>` with the actual tunnel ID from step 1.4!**

### Step 1.6: Route DNS to the Tunnel

```bash
# Create DNS CNAME record for api subdomain
cloudflared tunnel route dns geo-content-backend api.geoaction.tocanan.ai
```

**Expected output:**
```
2024-xx-xx INF Added CNAME api.geoaction.tocanan.ai which will route to this tunnel
```

This automatically creates a CNAME record in your Cloudflare DNS pointing to the tunnel.

### Step 1.7: Install and Start the Tunnel Service

```bash
# Install as systemd service
sudo cloudflared service install

# Start the service
sudo systemctl start cloudflared

# Enable to start on boot
sudo systemctl enable cloudflared

# Check status
sudo systemctl status cloudflared
```

**Expected status output:**
```
● cloudflared.service - cloudflared
     Loaded: loaded (/etc/systemd/system/cloudflared.service; enabled)
     Active: active (running) since ...
```

### Step 1.8: Verify Tunnel is Working

```bash
# Test from EC2 that tunnel is routing
curl -H "Host: api.geoaction.tocanan.ai" http://localhost:80/api/v1/health

# Should return:
# {"status":"healthy","service":"geo-content-platform",...}
```

**If this works, the tunnel is correctly configured!**

---

## Part 2: Update Backend CORS Configuration on EC2

### Step 2.1: Update systemd Service File

```bash
# Edit the systemd service file
sudo nano /etc/systemd/system/geo-content.service
```

**Find the line with `Environment=CORS_ORIGINS=` and update it to:**

```ini
Environment=CORS_ORIGINS=https://geoaction.tocanan.ai,http://localhost:3000
```

**Save and exit:** `Ctrl+X`, then `Y`, then `Enter`

### Step 2.2: Restart the Backend Service

```bash
# Reload systemd configuration
sudo systemctl daemon-reload

# Restart the service
sudo systemctl restart geo-content

# Check status
sudo systemctl status geo-content

# Verify it's running
sudo journalctl -u geo-content -f
```

**Press `Ctrl+C` to exit log viewing.**

### Step 2.3: Test Backend from External Network

```bash
# From your local machine (not EC2), test the API through the tunnel
curl https://api.geoaction.tocanan.ai/api/v1/health
```

**Expected response:**
```json
{"status":"healthy","service":"geo-content-platform","version":"3.2.0",...}
```

**If you get a response, the tunnel is working correctly!**

---

## Part 3: Configure Cloudflare Zero Trust Applications

### Step 3.1: Access Cloudflare Zero Trust Dashboard

1. Go to: https://one.dash.cloudflare.com/
2. Select your Cloudflare account
3. Navigate to: **Access** → **Applications**

### Step 3.2: Create Backend API Application

Click **"Add an application"** → **"Self-hosted"**

#### Application Configuration

| Field | Value |
|-------|-------|
| **Application name** | GEO Content Platform - Backend |
| **Session Duration** | 24 hours |
| **Application domain** | |
| - Subdomain | `api.geoaction` |
| - Domain | `tocanan.ai` |

**Leave Path empty**

#### Add Policy

Click **"Add a policy"**

| Setting | Value |
|---------|-------|
| **Policy name** | Allow Authenticated Users |
| **Action** | Allow |
| **Session duration** | 24 hours |

#### Configure Rules

Under **"Configure rules"**, add:

**Include:**
- Select **"Emails"** and add your email addresses (e.g., `eden.lau@tocanan.com`)
- OR select **"Email domain"** and add `tocanan.com` to allow all @tocanan.com emails
- OR select **"Everyone"** for open access (requires authentication)

**Example for corporate access:**
```
Include:
  Emails ending in: @tocanan.com
```

Click **"Save policy"** and **"Save application"**

### Step 3.3: Create Frontend Application

Click **"Add an application"** → **"Self-hosted"**

#### Application Configuration

| Field | Value |
|-------|-------|
| **Application name** | GEO Content Platform - Frontend |
| **Session Duration** | 24 hours |
| **Application domain** | |
| - Subdomain | `geoaction` |
| - Domain | `tocanan.ai` |

#### Add Policy (Same as Backend)

| Setting | Value |
|---------|-------|
| **Policy name** | Allow Authenticated Users |
| **Action** | Allow |
| **Session duration** | 24 hours |

**Include:** Same rules as backend (email domain: tocanan.com)

Click **"Save policy"** and **"Save application"**

### Step 3.4: Configure Identity Provider

Navigate to: **Settings** → **Authentication**

#### Enable One-time PIN (Simplest)

1. Find **"One-time PIN"** in the login methods
2. Toggle to **"Enable"**
3. Save changes

**This allows users to:**
- Enter their email address
- Receive a 6-digit code via email
- Enter the code to authenticate
- Session valid for 24 hours

#### Optional: Add Additional Providers

You can also enable:
- **Google Workspace** (for corporate Google accounts)
- **Microsoft Entra ID** (for Azure AD/Office 365)
- **Okta, Auth0, etc.** (Enterprise SSO)

---

## Part 4: Configure DNS in Cloudflare

### Step 4.1: Access Cloudflare DNS Dashboard

1. Go to: https://dash.cloudflare.com/
2. Select **tocanan.ai** domain
3. Navigate to: **DNS** → **Records**

### Step 4.2: Verify/Add DNS Records

You should see these records (the `api` record was auto-created by cloudflared):

| Type | Name | Content | Proxy Status | TTL |
|------|------|---------|--------------|-----|
| CNAME | api | \<TUNNEL-ID\>.cfargotunnel.com | ☁️ Proxied | Auto |
| CNAME | geoaction | geo-content-frontend-053955129008.s3-website-ap-southeast-1.amazonaws.com | ☁️ Proxied | Auto |

**If the `geoaction` record doesn't exist, create it:**

1. Click **"Add record"**
2. **Type:** CNAME
3. **Name:** geoaction
4. **Target:** geo-content-frontend-053955129008.s3-website-ap-southeast-1.amazonaws.com
5. **Proxy status:** ☁️ Proxied (orange cloud) - **IMPORTANT: Must be enabled!**
6. **TTL:** Auto
7. Click **"Save"**

**CRITICAL:** Both records MUST have the orange cloud (Proxied) enabled!

---

## Part 5: Testing & Validation

### Step 5.1: Test Backend API (Without Authentication)

**Temporarily disable the Zero Trust application to test routing:**

1. Go to: Cloudflare Zero Trust → Access → Applications
2. Find **"GEO Content Platform - Backend"**
3. Toggle to **"Disable"**

**Test from your local machine:**

```bash
curl https://api.geoaction.tocanan.ai/api/v1/health
```

**Expected response:**
```json
{"status":"healthy","service":"geo-content-platform","version":"3.2.0"}
```

**If this works, re-enable the application:**

1. Toggle back to **"Enable"**

### Step 5.2: Test Frontend Access

1. Open browser (use incognito mode for clean test)
2. Navigate to: **https://geoaction.tocanan.ai**

**Expected flow:**

1. **Cloudflare Access Login Page Appears**
   - You should see Cloudflare Access authentication
   - NOT the React app directly

2. **Enter Your Email Address**
   - Enter an email that matches your policy (e.g., eden.lau@tocanan.com)

3. **Check Email for Code**
   - You should receive a 6-digit code
   - Subject: "Verify your identity"

4. **Enter the Code**
   - Input the 6-digit code on the verification page

5. **Redirected to Frontend**
   - You should now see the GEO Content Platform React app

### Step 5.3: Test API Connectivity

**Once authenticated and viewing the frontend:**

1. **Open Browser DevTools**
   - Press `F12` or right-click → Inspect

2. **Check Console Tab**
   - Look for any errors
   - Should see: `[API] GET /health` or similar
   - Should NOT see CORS errors

3. **Check Network Tab**
   - Clear the network log
   - Refresh the page
   - Verify requests to `https://api.geoaction.tocanan.ai/api/v1/health` succeed
   - Status should be `200 OK`

4. **Test Content Generation**
   - Fill out the content generation form:
     - Client Name: Test Client
     - Target Question: What is cloud computing?
     - Word Count: 300
   - Click **"Generate Content"**
   - Watch the Network tab:
     - Should see POST to `https://api.geoaction.tocanan.ai/api/v1/generate/async`
     - Should see GET to `https://api.geoaction.tocanan.ai/api/v1/jobs/<job_id>`
   - Verify generation completes successfully
   - Verify GEO Insights render correctly

### Step 5.4: Test Session Persistence

1. **Close the browser tab**
2. **Open a new tab**
3. **Navigate to:** https://geoaction.tocanan.ai

**Expected:** You should be automatically logged in (no authentication prompt) because your session is valid for 24 hours.

### Step 5.5: Test from Different Network

1. **Test from mobile device** (different network)
2. **Test from VPN connection**
3. **Verify authentication works from all networks**

---

## Part 6: Monitoring & Troubleshooting

### Monitor Cloudflare Access Logs

**Cloudflare Dashboard** → **Zero Trust** → **Logs** → **Access**

View:
- Authentication attempts
- Blocked requests
- Allowed requests
- Session information

### Monitor Tunnel Logs (on EC2)

```bash
# View real-time tunnel logs
sudo journalctl -u cloudflared -f

# Check tunnel status
cloudflared tunnel info geo-content-backend

# List all tunnel routes
cloudflared tunnel route list
```

### Monitor Backend Logs (on EC2)

```bash
# FastAPI application logs
sudo journalctl -u geo-content -f

# Nginx access logs
sudo tail -f /var/log/nginx/geo_content_access.log

# Nginx error logs
sudo tail -f /var/log/nginx/geo_content_error.log
```

---

## Troubleshooting Common Issues

### Issue: "502 Bad Gateway"

**Cause:** Tunnel can't reach backend or backend is down

**Check:**
```bash
# On EC2
sudo systemctl status cloudflared
sudo systemctl status geo-content
curl http://localhost:80/api/v1/health
```

**Fix:**
```bash
sudo systemctl restart cloudflared
sudo systemctl restart geo-content
```

### Issue: "CORS Error" in Browser Console

**Symptoms:** Console shows: `Access to fetch at 'https://api.geoaction.tocanan.ai' from origin 'https://geoaction.tocanan.ai' has been blocked by CORS policy`

**Check:**
```bash
# On EC2, verify CORS configuration
sudo systemctl status geo-content
sudo journalctl -u geo-content | grep -i cors
```

**Fix:**
```bash
# Ensure systemd service has correct CORS_ORIGINS
sudo nano /etc/systemd/system/geo-content.service

# Verify this line exists:
# Environment=CORS_ORIGINS=https://geoaction.tocanan.ai,http://localhost:3000

# Restart service
sudo systemctl daemon-reload
sudo systemctl restart geo-content
```

### Issue: "API Offline" in Frontend UI

**Symptoms:** Frontend shows red "API Offline" indicator in header

**Check:**
```bash
# Test API directly
curl https://api.geoaction.tocanan.ai/api/v1/health
```

**If curl works but frontend shows offline:**
1. Open DevTools → Console
2. Check for specific error messages
3. Verify `VITE_API_BASE_URL` in built files:
   ```bash
   # On local machine
   cd frontend/dist/assets
   grep -r "api.geoaction.tocanan.ai" .
   ```

**Fix:**
- Rebuild and redeploy frontend if URL is incorrect
- Clear browser cache and hard refresh (`Cmd+Shift+R` or `Ctrl+Shift+R`)

### Issue: "Cloudflare Access Redirect Loop"

**Symptoms:** Browser keeps redirecting between Cloudflare Access and your app

**Check:**
1. Cloudflare Zero Trust → Applications
2. Verify application domains are correct:
   - Frontend: `geoaction.tocanan.ai` (no path)
   - Backend: `api.geoaction.tocanan.ai` (no path)

**Fix:**
- Temporarily disable Zero Trust app
- Test if tunnel works without auth (curl https://api.geoaction.tocanan.ai/api/v1/health)
- If tunnel works, re-enable and check application domain settings

### Issue: "Mixed Content" Error

**Symptoms:** Browser console shows: `Mixed Content: The page was loaded over HTTPS, but requested an insecure resource`

**Cause:** Frontend trying to make HTTP requests instead of HTTPS

**Check:**
```bash
# On local machine, check .env.production
cat frontend/.env.production

# Should show:
# VITE_API_BASE_URL=https://api.geoaction.tocanan.ai
```

**Fix:**
- Ensure `VITE_API_BASE_URL` starts with `https://`
- Rebuild and redeploy frontend

### Issue: Frontend Shows 404 on SPA Routes

**Symptoms:** Direct navigation to routes like `/results` shows 404

**Cause:** S3 static website hosting doesn't handle SPA routing

**Fix:**

Option 1: Configure S3 error handling
```bash
AWS_PROFILE=eden.lau.dev aws s3 website s3://geo-content-frontend-053955129008/ \
  --index-document index.html \
  --error-document index.html
```

Option 2: Use Cloudflare Workers (advanced)
- Create a Worker to rewrite 404s to index.html

---

## Success Checklist

- ✅ Cloudflared tunnel installed and running on EC2
- ✅ DNS records created (api.geoaction.tocanan.ai, geoaction.tocanan.ai)
- ✅ Backend CORS updated to include https://geoaction.tocanan.ai
- ✅ Frontend deployed to S3 with new API URL
- ✅ Cloudflare Zero Trust applications created for both frontend and backend
- ✅ Identity provider enabled (One-time PIN)
- ✅ Can access https://geoaction.tocanan.ai and authenticate
- ✅ API health check works: https://api.geoaction.tocanan.ai/api/v1/health
- ✅ No CORS errors in browser console
- ✅ Content generation works end-to-end

---

## Maintenance Tasks

### Updating Backend Code

```bash
# On EC2
cd /opt/geo_content
git pull origin main
/root/.local/bin/uv sync
sudo systemctl restart geo-content
sudo journalctl -u geo-content -f
```

### Updating Frontend Code

```bash
# On local machine
cd frontend
npm run build

AWS_PROFILE=eden.lau.dev aws s3 sync dist/ s3://geo-content-frontend-053955129008/ \
  --delete \
  --region ap-southeast-1 \
  --cache-control "max-age=31536000" \
  --exclude "index.html"

AWS_PROFILE=eden.lau.dev aws s3 cp dist/index.html s3://geo-content-frontend-053955129008/index.html \
  --region ap-southeast-1 \
  --cache-control "no-cache, no-store, must-revalidate"
```

### Restart Cloudflared Tunnel

```bash
# On EC2
sudo systemctl restart cloudflared
sudo systemctl status cloudflared
sudo journalctl -u cloudflared -f
```

---

## Security Considerations

### Access Control

- **Current Setup:** Email-based authentication (One-time PIN)
- **Recommended:** Add email domain restriction (only @tocanan.com)
- **Enterprise:** Use SSO (Google Workspace, Microsoft Entra ID)

### Session Management

- **Current:** 24-hour session duration
- **Consider:** Shorter sessions for sensitive operations
- **Monitor:** Check access logs regularly for unauthorized attempts

### Network Security

- **EC2 Security Group:** Ports 22, 80, 443 are open
- **Recommendation:** Restrict port 22 (SSH) to specific IPs
- **Tunnel Security:** All traffic to backend goes through Cloudflare Tunnel (secure)

---

## Contact & Support

**Platform URL:** https://geoaction.tocanan.ai

**For technical issues:**
- Check this troubleshooting guide first
- Review Cloudflare Access logs
- Check backend logs on EC2

**Documentation:**
- [DEPLOYMENT_COMPLETE.md](DEPLOYMENT_COMPLETE.md) - Original deployment guide
- [DEPLOYMENT_INSTRUCTIONS.md](DEPLOYMENT_INSTRUCTIONS.md) - Infrastructure setup
- [GEO_ACTION_USER_GUIDE.md](/tmp/GEO_ACTION_USER_GUIDE.md) - End-user guide

---

## Next Steps

After successful deployment:

1. **Test thoroughly** with real users
2. **Monitor access logs** for any issues
3. **Set up alerts** in Cloudflare for failed authentication
4. **Document any custom configurations** for your team
5. **Consider migrating to Cloudflare Pages** for long-term (simpler deployment)

---

**Deployment Date:** December 2, 2025
**Version:** 1.0
**Platform:** GEO Content Optimization Platform v3.2.0
