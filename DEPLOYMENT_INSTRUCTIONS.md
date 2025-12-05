# GEO Content Platform - Enhanced Insights Deployment

## Overview
This deployment adds comprehensive GEO insights to help users maximize content performance. The new features include:

1. **Implementation Checklist** - Prioritized actionable items with estimated impact
2. **Source Quality Analysis** - Credibility assessment of research sources
3. **Keyword & Entity Analysis** - Optimization recommendations for entity mentions
4. **Benchmark Comparison** - Performance vs. top-ranking content
5. **Content Structure Score** - AI parsing optimization analysis
6. **Enhanced Schema Markup** - Multiple schema types (Article, FAQ, HowTo)
7. **Multi-Format Export** - HTML, Markdown, Plain Text, JSON-LD

## Backend Deployment (EC2)

### Step 1: SSH into EC2 Instance

```bash
# Use your SSH key for the harbour-city-data-processing key pair
ssh -i ~/.ssh/your-key.pem ubuntu@18.138.26.110
```

### Step 2: Download Updates from S3

```bash
# Download the updates package
cd /opt/geo_content
aws s3 cp s3://geo-content-uploads-053955129008/deployments/geo_updates.tar.gz /tmp/

# Extract the updates
cd /opt/geo_content
tar xzf /tmp/geo_updates.tar.gz

# Verify files were extracted
ls -la src/geo_content/models/geo_insights.py
ls -la src/geo_content/tools/geo_analyzers.py
ls -la src/geo_content/tools/format_exporters.py
```

### Step 3: Restart the Backend Service

```bash
# Restart uvicorn service
sudo systemctl restart geo-content

# Check service status
sudo systemctl status geo-content

# Monitor logs for any errors
sudo journalctl -u geo-content -f --lines=50
```

### Step 4: Verify Backend Health

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test a generation (should now include geo_insights in response)
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "Test Client",
    "target_question": "What are the benefits of cloud computing?",
    "target_word_count": 300
  }'
```

## Frontend Deployment (S3)

### Step 1: Build Frontend Locally

```bash
# Navigate to frontend directory
cd /Users/edenlau/Desktop/data_scien:Users:edenlau:Library:CloudStorage:OneDrive-tocanan.com:Team\ Share\ Folder\ -\ Corp\ PPT\ \&\ Artwork:Tocanan\ logo\ PNG\ files:Tocanan_logo_Social\ Media\ copy.jpegce_projects_local/geo_content/frontend

# Install dependencies (if needed)
npm install

# Build for production
npm run build
```

### Step 2: Deploy to S3

```bash
# Sync build to S3 bucket
AWS_PROFILE=eden.lau.dev aws s3 sync dist/ s3://geo-content-frontend-053955129008 --delete --region ap-southeast-1

# Verify deployment
AWS_PROFILE=eden.lau.dev aws s3 ls s3://geo-content-frontend-053955129008/
```

### Step 3: Test Frontend

Open the frontend URL in your browser:
```
http://geo-content-frontend-053955129008.s3-website-ap-southeast-1.amazonaws.com
```

## Verification Checklist

After deployment, verify:

- [ ] Backend service is running (`sudo systemctl status geo-content`)
- [ ] Health endpoint responds (`curl http://localhost:8000/health`)
- [ ] Test generation completes successfully
- [ ] Response includes `geo_insights` field
- [ ] Frontend loads without errors (check browser console)
- [ ] Frontend displays new "GEO Insights" sections after content generation
- [ ] All 5 insight cards render correctly:
  - Implementation Checklist
  - Benchmark Comparison
  - Keyword & Entity Optimization
  - Source Quality Analysis
  - Content Structure

## Expected Output Structure

The API response should now include a `geo_insights` field with this structure:

```json
{
  "geo_insights": {
    "implementation_checklist": {
      "actions": [
        {
          "priority": "high",
          "category": "citations",
          "action": "Add authoritative source links",
          "impact": "Increases E-E-A-T Trust score by 15-20%",
          "example": "Add inline links to official government statistics",
          "current_gap": "0 citations found"
        }
      ],
      "total_estimated_impact": "+40-60%"
    },
    "benchmark_comparison": {
      "target_metrics": {
        "statistics_count": {
          "current": 3,
          "target": 5,
          "gap": -2,
          "status": "behind"
        }
      },
      "overall_competitiveness": 72
    },
    "keyword_analysis": { ... },
    "source_analysis": { ... },
    "structure_analysis": { ... }
  }
}
```

## Rollback Plan

If issues occur:

### Backend Rollback
```bash
# On EC2, restore from git
cd /opt/geo_content
git checkout HEAD -- src/

# Restart service
sudo systemctl restart geo-content
```

### Frontend Rollback
```bash
# Locally, checkout previous version and rebuild
cd frontend
git checkout HEAD~1 -- src/
npm run build

# Redeploy to S3
AWS_PROFILE=eden.lau.dev aws s3 sync dist/ s3://geo-content-frontend-053955129008 --delete --region ap-southeast-1
```

## Troubleshooting

### Backend Issues

**Import Errors:**
```bash
# Check Python environment
cd /opt/geo_content
source .venv/bin/activate
python -c "from geo_content.models.geo_insights import GEOInsights; print('OK')"
python -c "from geo_content.tools.geo_analyzers import geo_insights_analyzer; print('OK')"
```

**Service Won't Start:**
```bash
# Check logs
sudo journalctl -u geo-content -n 100 --no-pager

# Test manually
cd /opt/geo_content
source .venv/bin/activate
uvicorn geo_content.api:app --host 0.0.0.0 --port 8000
```

### Frontend Issues

**TypeScript Compilation Errors:**
```bash
cd frontend
npm run type-check
```

**Component Not Displaying:**
- Check browser console for errors
- Verify `result.geo_insights` exists in API response
- Check network tab for API response structure

## Performance Considerations

The new analyzers add minimal overhead (~200-500ms per generation):
- Implementation checklist: ~50ms
- Source analysis: ~100ms
- Keyword analysis: ~100ms
- Benchmark comparison: ~50ms
- Structure analysis: ~100ms
- Schema generation: ~50ms

Total additional latency: ~450ms on top of existing generation time.

## Support

If you encounter issues:
1. Check logs: `sudo journalctl -u geo-content -f`
2. Verify all files were deployed correctly
3. Test with a simple generation request
4. Check browser console for frontend errors
