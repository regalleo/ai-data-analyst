# AI Data Analyst - Render Deployment Guide

This guide covers deploying your AI Data Analyst backend to Render.com.

## Why Render?

- ✅ Free tier available (750 hours/month)
- ✅ Easy PostgreSQL integration
- ✅ Simple configuration
- ✅ Good documentation
- ✅ Automatic HTTPS

---

## Architecture on Render

```
Frontend (Vercel) → Backend (Render) → PostgreSQL (Render)
                         ↓
                  AI Services (Groq)
```

---

## Step-by-Step Deployment

### Prerequisites

1. Render account: https://render.com (sign up with GitHub)
2. GitHub repository with your code pushed
3. Groq API key: https://console.groq.com

---

### Step 1: Create PostgreSQL Database on Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "PostgreSQL"
3. Configure:
   ```
   Name: ai-analyst-db
   Database: ai_analytics
   User: ai_analyst
   Region: Choose closest to your users
   ```
4. Click "Create Database"
5. **IMPORTANT**: Copy the "Internal Database URL" after creation
   - Format: `postgres://user:password@host:5432/database`

---

### Step 2: Deploy Backend Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:

   ```
   Name: ai-analyst-backend
   Root Directory: backend
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

5. Click "Create Web Service"

---

### Step 3: Configure Environment Variables

After the service is created, go to "Environment" tab and add:

| Variable | Value | Required |
|----------|-------|----------|
| `DATABASE_URL` | `postgres://user:pass@host:5432/ai_analytics` | ✅ Yes |
| `GROQ_API_KEY` | `gsk_xxxxxxxxxxxxxxxxxxxxxxxx` | ✅ Yes |
| `SECRET_KEY` | `your-32-char-minimum-secret-key` | ✅ Yes |
| `OPENAI_API_KEY` | `sk-xxxxxxxxxxxxxxxxxxxxxxxx` | ❌ Optional |

**To generate SECRET_KEY:**
```bash
openssl rand -base64 32
```

---

### Step 4: Initialize Database Schema

Option A: Use Render's PostgreSQL Shell
1. Go to your PostgreSQL database in Render dashboard
2. Click "Connect" → "Shell"
3. Run:
   ```sql
   -- Copy content from backend/schema.sql and paste here
   ```

Option B: Use psql locally
```bash
# Get connection string from Render dashboard
export DATABASE_URL="postgres://..."

# Run schema
psql "$DATABASE_URL" -f backend/schema.sql
```

---

### Step 5: Configure Health Check

In your web service settings:

```
Health Check Path: /
Health Check Timeout: 30s
```

---

### Step 6: Update CORS for Production

Before deploying, update `backend/main.py` to restrict CORS:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.vercel.app"],  # Your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### Step 7: Redeploy

1. Go to your web service in Render dashboard
2. Click "Deploy" → "Deploy Latest Commit"
3. Wait for deployment to complete

---

## Verifying Deployment

### Test Health Endpoint
```bash
curl https://your-service.onrender.com/
```

Expected response:
```json
{"status": "ok", "service": "AI Data Analyst"}
```

### Test API Docs
Visit: `https://your-service.onrender.com/docs`

### Test Registration
```bash
curl -X POST https://your-service.onrender.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'psycopg2'"
- Ensure `psycopg2-binary` is in `requirements.txt`
- Redeploy after adding

### "connection refused" to database
- Check `DATABASE_URL` format
- Ensure PostgreSQL is fully provisioned (wait 1-2 minutes)
- Verify SSL: Add `?sslmode=require` to connection string

### "GROQ_API_KEY not found"
- Add variable in Environment tab
- Redeploy after adding

### Service won't start
- Check "Logs" tab in Render dashboard
- Common issues:
  - Missing dependencies
  - Wrong Python version
  - Port not accessible

### Timeout on startup
- Increase startup timeout in settings
- Reduce initial data loading

---

## Performance Tips

### Free Tier Limitations
- 750 hours/month (enough for 1 service)
- 512 MB RAM
- Shared CPU
- Sleep after 15 minutes of inactivity

### Keep Awake (Paid Feature)
- Upgrade to paid plan for always-on
- Or use a cron job to ping the service

### Speed Up Deployments
```txt
# In requirements.txt - use minimal packages
# Only install what you need
```

---

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection | `postgres://user:pass@host:5432/db` |
| `GROQ_API_KEY` | LLM API key | `gsk_xxxxxxxxxxxx` |
| `SECRET_KEY` | JWT signing key | `abc123...` (32+ chars) |
| `OPENAI_API_KEY` | Optional: OpenAI | `sk-xxxxxxxxxxxx` |
| `PORT` | Auto-set by Render | `10000` |
| `PYTHON_VERSION` | Python version | `3.11` |

---

## Render CLI (Optional)

### Install
```bash
npm install -g render-cli
render login
```

### Deploy
```bash
render deploy --service ai-analyst-backend
```

### View Logs
```bash
render logs --service ai-analyst-backend
```

---

## Cost Estimation

| Resource | Free Tier | Paid |
|----------|-----------|------|
| Web Service | 750 hrs/month | $7/month |
| PostgreSQL | 1 GB storage | $7/month |
| **Total** | **$0/month** | **$14/month** |

---

## Alternative: render.yaml Configuration

Create `backend/render.yaml` for programmatic deployment:

```yaml
services:
  - type: web
    name: ai-analyst-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: ai-analyst-db
          property: connectionString
      - key: GROQ_API_KEY
        sync: false
      - key: SECRET_KEY
        sync: false

databases:
  - name: ai-analyst-db
    databaseName: ai_analytics
    plan: free
```

Deploy with:
```bash
render deploy --spec render.yaml
```

---

## Next Steps

1. ✅ Deploy backend to Render
2. 🔲 Update frontend API URL to Render backend
3. 🔲 Deploy frontend to Vercel
4. 🔲 Test end-to-end functionality

---

## Resources

- [Render Docs](https://render.com/docs)
- [Render Discord](https://discord.gg/render)
- [Python on Render](https://render.com/docs/python)
- [PostgreSQL on Render](https://render.com/docs/postgresql)

---

**Last Updated**: 2024
**Version**: 1.0.0

