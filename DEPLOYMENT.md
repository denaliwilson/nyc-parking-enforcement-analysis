# Deployment Guide

## Streamlit Community Cloud Deployment

This guide covers deploying the NYC Parking Citations Dashboard to Streamlit Community Cloud (free hosting).

## Prerequisites

✅ GitHub account  
✅ Repository pushed to GitHub  
✅ Streamlit Community Cloud account (free at [share.streamlit.io](https://share.streamlit.io))

---

## Pre-Deployment Checklist

### 1. Verify Required Files

Ensure these files exist in your repository root:

- ✅ `dashboard.py` - Main application file
- ✅ `requirements.txt` - Python dependencies
- ✅ `packages.txt` - System dependencies (should be empty)
- ✅ `.streamlit/config.toml` - Theme configuration (optional)

### 2. Verify Requirements.txt

Your `requirements.txt` should have Streamlit-compatible versions:

```txt
# Core dependencies
pandas>=2.0.0,<3.0.0          # Streamlit requires pandas 2.x
numpy>=1.24.0,<2.0.0
requests>=2.31.0

# Geospatial (no system dependencies needed)
geopandas==0.14.1
shapely>=2.0.0,<3.0.0
pyproj>=3.6.0,<4.0.0

# Visualization
plotly>=5.17.0
streamlit>=1.28.0

# Utilities
python-dotenv>=1.0.0
```

### 3. Verify packages.txt

Your `packages.txt` should be **completely empty** (no comments, no packages):

```txt

```

**Why empty?** This project uses pure Python geospatial libraries that don't require system packages, avoiding dependency conflicts in cloud environments.

---

## Deployment Steps

### Step 1: Prepare Repository

```bash
# Add all changes
git add .

# Commit
git commit -m "Prepare for Streamlit Cloud deployment"

# Push to GitHub
git push origin main
```

### Step 2: Connect to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Authorize Streamlit to access your repositories

### Step 3: Deploy New App

1. Click **"New app"** button
2. Fill in deployment settings:
   - **Repository**: Select your `nyc-parking-enforcement-analysis` repo
   - **Branch**: `main` (or your default branch)
   - **Main file path**: `dashboard.py`
   - **App URL**: Choose a custom subdomain (e.g., `nyc-parking-dashboard`)

3. Click **"Deploy!"**

### Step 4: Monitor Deployment

**Deployment Phases:**
1. 🐙 **Pulling code** (~10 seconds) - Clones your repository
2. 📦 **Processing dependencies** (~2-3 minutes) - Installs packages
3. 🚀 **Starting app** (~30 seconds) - Launches Streamlit server

**Watch the logs** for any errors during installation.

### Step 5: Verify Deployment

Once deployed, your app will be available at:
```
https://your-app-name.streamlit.app
```

Test the following:
- ✅ Landing page loads with hero image
- ✅ Latest date detection works
- ✅ Date selector appears
- ✅ "Load Data" button functions
- ✅ Maps render correctly
- ✅ Borough/precinct drill-down works

---

## Troubleshooting

### Issue: Dependency Installation Fails

**Symptom:** `installer returned a non-zero exit code`

**Solutions:**
1. **Check requirements.txt** - Ensure no incompatible versions
2. **Verify packages.txt is empty** - No comments, no whitespace
3. **Delete and recreate app** - Sometimes the environment gets corrupted
4. **Check logs** - Look for specific package errors

### Issue: "Unable to locate package" Error

**Symptom:** `E: Unable to locate package <word-from-comment>`

**Cause:** packages.txt contains comments or text (apt-get tries to install each word as a package)

**Solution:**
```bash
# Make packages.txt completely empty
echo > packages.txt
git add packages.txt
git commit -m "Fix packages.txt - must be empty"
git push
```

### Issue: "Unmet dependencies" Error

**Symptom:** `libgdal32 : Depends: libodbc2 but it is not installed`

**Cause:** Broken package state from previous deployment attempts

**Solution:**
1. Delete the app from Streamlit Cloud
2. Wait 5 minutes for cleanup
3. Redeploy as a new app (fresh environment)

### Issue: GeoPandas Import Error

**Symptom:** `ModuleNotFoundError: No module named 'geopandas'`

**Solution:** Check that requirements.txt includes:
```txt
geopandas==0.14.1
shapely>=2.0.0,<3.0.0
pyproj>=3.6.0,<4.0.0
```

### Issue: Map Not Rendering

**Symptom:** Blank map or "No geometry" error

**Cause:** GeoJSON file not loading correctly

**Solution:** Dashboard auto-downloads NYC precinct boundaries on first load. Check logs for API errors.

---

## Automatic Redeployment

After initial deployment, **every git push automatically triggers redeployment**:

```bash
# Make changes locally
# ... edit files ...

# Commit and push
git add .
git commit -m "Update dashboard features"
git push

# Streamlit Cloud automatically redeploys (1-2 minutes)
```

**No manual action needed** - just push to GitHub!

---

## Environment Variables (Optional)

If you need API tokens or secrets:

1. Go to your app settings on Streamlit Cloud
2. Click **"Secrets"** in the left sidebar
3. Add secrets in TOML format:

```toml
# .streamlit/secrets.toml format
NYC_API_TOKEN = "your-api-token-here"
```

Access in code:
```python
import streamlit as st
api_token = st.secrets["NYC_API_TOKEN"]
```

---

## Performance Optimization

### Enable Caching

The dashboard uses Streamlit caching for performance:

```python
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_latest_available_date():
    # Expensive API call cached
    ...

@st.cache_resource
def get_loader():
    # Resource cached for session
    ...
```

### Monitor Usage

- Streamlit Community Cloud includes **1 GB RAM** per app
- **CPU usage** is shared
- **Bandwidth** is generous for typical use

**Tip:** The dashboard loads data incrementally to stay within limits.

---

## Custom Domain (Optional)

To use your own domain:

1. Upgrade to Streamlit Teams ($250/month)
2. Or use a reverse proxy (e.g., Nginx, Cloudflare) pointing to your `.streamlit.app` URL

---

## Updating the Deployment

### Code Changes
```bash
git add .
git commit -m "Your change description"
git push  # Auto-deploys
```

### Dependency Changes
```bash
# Edit requirements.txt
vim requirements.txt

# Commit and push
git add requirements.txt
git commit -m "Update dependencies"
git push  # Triggers full rebuild
```

### Theme Changes
```bash
# Edit .streamlit/config.toml
vim .streamlit/config.toml

# Commit and push
git add .streamlit/config.toml
git commit -m "Update theme"
git push  # Updates immediately
```

---

## Rollback

If deployment breaks:

1. **Identify last working commit:**
   ```bash
   git log --oneline
   ```

2. **Revert to that commit:**
   ```bash
   git revert <commit-hash>
   git push
   ```

3. **Or force push previous version:**
   ```bash
   git reset --hard <commit-hash>
   git push --force
   ```

Streamlit Cloud will automatically redeploy the reverted version.

---

## Monitoring and Logs

### View Logs
1. Go to your app on Streamlit Cloud
2. Click **"Manage app"** (⋮ menu)
3. View real-time logs in the dashboard

### Metrics
- **App status**: Running / Sleeping / Error
- **Last deployed**: Timestamp
- **Memory usage**: Current RAM usage
- **Active users**: Number of concurrent sessions

---

## Best Practices

✅ **Test locally first** - Always test with `streamlit run dashboard.py` before pushing  
✅ **Keep dependencies minimal** - Only include packages you actually use  
✅ **Use caching** - Cache expensive operations (`@st.cache_data`)  
✅ **Handle errors gracefully** - Show user-friendly error messages  
✅ **Monitor logs** - Check deployment logs for warnings  
✅ **Version control** - Tag releases for easy rollback  

---

## Support

- **Streamlit Docs**: https://docs.streamlit.io
- **Community Forum**: https://discuss.streamlit.io
- **GitHub Issues**: Report issues in your repository

---

## Cost

**Streamlit Community Cloud:**
- ✅ Free forever
- ✅ Unlimited public apps
- ✅ 1 GB RAM per app
- ✅ Automatic SSL certificates
- ✅ GitHub integration

**Limitations:**
- Apps sleep after 7 days of inactivity (wake on visit)
- Public visibility (anyone can access)
- Shared compute resources

**Upgrade to Streamlit Teams** if you need:
- Private apps
- More resources
- Custom domains
- Priority support
