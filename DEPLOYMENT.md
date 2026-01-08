# AI Data Analyst - Complete Deployment Guide

This guide covers deploying your AI Data Analyst application to production with free-tier friendly services.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        PRODUCTION DEPLOYMENT                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│   │   Frontend   │    │   Backend    │    │   Database   │     │
│   │   (Vercel)   │───▶│  (Railway)   │───▶│  (Neon PG)   │     │
│   └──────────────┘    └──────────────┘    └──────────────┘     │
│         │                   │                   │               │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│   ┌──────────────────────────────────────────────────────┐     │
│   │              AI Services (Groq API)                   │     │
│   └──────────────────────────────────────────────────────┘     │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Deploy (5 Minutes)

### 1. Deploy Database (Neon - Free PostgreSQL)

1. Go to [Neon.tech](https://neon.tech) and sign up with GitHub
2. Create a new project:
   - Name: `ai-analyst-prod`
   - Region: Choose closest to your users
3. Copy your connection string:
   ```
   postgresql://user:password@ep-xxx.us-east-1.aws.neon.tech/ai_analytics?sslmode=require
   ```
4. Add `?sslmode=require` at the end for production

### 2. Deploy Backend (Railway - Free)

1. Go to [Railway.app](https://railway.app) and sign up with GitHub
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your `ai-data-analyst` repository
4. Add environment variables in Railway dashboard:

   ```env
   # Required
   DATABASE_URL=postgresql://user:password@ep-xxx.us-east-1.aws.neon.tech/ai_analytics?sslmode=require
   GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxx
   SECRET_KEY=your-super-secret-key-min-32-characters-long
   
   # Optional (for enhanced features)
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
   ```

5. Deploy! Railway will automatically install dependencies from `requirements.txt`

### 3. Deploy Frontend (Vercel - Free)

1. Go to [Vercel.com](https://vercel.com) and sign up with GitHub
2. Click "Add New..." → "Project"
3. Import your `ai-data-analyst` repository
4. Configure settings:
   - Framework Preset: `Next.js`
   - Root Directory: `frontend`
5. Add environment variables:

   ```env
   NEXT_PUBLIC_API_URL=https://your-backend.railway.app
   ```

6. Deploy! Vercel will build and deploy your Next.js app

---

## Detailed Step-by-Step Guide

### Prerequisites

```bash
# Install Railway CLI for local development
curl -fsSL https://railway.app/install.sh | sh

# Install Vercel CLI
npm i -g vercel

# Install Neon CLI (optional)
npm install -g neon-cli
```

### Step 1: Database Setup (Neon PostgreSQL)

#### Option A: Via Neon Dashboard (Recommended)

1. Create account at [Neon.tech](https://neon.tech)
2. Create new project:
   ```
   Project name: ai-analyst-prod
   Database name: ai_analytics
   ```
3. Copy the connection string from the dashboard
4. The connection string will look like:
   ```
   postgresql://[user]:[password]@[host]/ai_analytics
   ```
5. Add `?sslmode=require` for production security

#### Option B: Via Command Line

```bash
# Install neon CLI
npm install -g neon-cli

# Create project
neon projects create --name ai-analyst-prod

# Create database
neon databases create --project-id <project-id> --name ai_analytics

# Get connection string
neon connection-string --project-id <project-id>
```

#### Initialize Database Schema

Once connected, run this SQL to create your tables:

```sql
-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create datasets table
CREATE TABLE IF NOT EXISTS datasets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    table_name VARCHAR(255) NOT NULL,
    owner_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    schema_info TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_datasets_owner ON datasets(owner_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
```

### Step 2: Backend Deployment (Railway)

#### Option A: Via Railway Dashboard

1. Go to [Railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Set root directory to `backend`
5. Add environment variables:

   ```env
   # Critical - Database Connection
   DATABASE_URL=postgresql://user:pass@host:5432/ai_analytics?sslmode=require
   
   # Security
   SECRET_KEY=your-32-character-minimum-secret-key-here
   
   # AI/LLM
   GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxx
   
   # Optional - For enhanced AI features
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
   
   # Python Runtime
   PYTHON_VERSION=3.11
   ```

6. Click "Deploy"

#### Option B: Via Railway CLI

```bash
# Login to Railway
railway login

# Initialize project
railway init

# Add PostgreSQL plugin
railway add postgresql

# Set environment variables
railway variables set DATABASE_URL="postgresql://..."
railway variables set GROQ_API_KEY="gsk_..."
railway variables set SECRET_KEY="your-secret-key"

# Deploy
railway up
```

#### Railway Configuration File

Create `backend/railway.json`:

```json
{
  "$schema": "https://railway.app/schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/",
    "healthcheckTimeout": 30,
    "restartPolicyType": "on-failure",
    "restartPolicyMaxRetries": 3
  }
}
```

#### Production Requirements.txt Update

Ensure your `backend/requirements.txt` has these production dependencies:

```txt
# Core
fastapi>=0.104.0
uvicorn[standard]>=0.24.0

# Database
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.9  # PostgreSQL driver

# Authentication
python-jose[cryptography]>=3.3.0
passlib==1.7.4
bcrypt==3.2.2
python-multipart>=0.0.6

# AI/LLM
langchain==0.3.22
langchain-core==0.3.56
langchain-community==0.3.20
langchain-groq==0.2.1
python-dotenv>=1.0.0

# Data Processing
numpy<2.0
pandas>=2.1.0,<2.2.0
numexpr>=2.8.0
bottleneck>=1.3.7

# Utilities
pydantic>=2.12.0
email-validator>=2.1.1
httpx>=0.25.0
```

### Step 3: Frontend Deployment (Vercel)

#### Option A: Via Vercel Dashboard

1. Go to [Vercel.com](https://vercel.com)
2. Click "Add New..." → "Project"
3. Import your GitHub repository
4. Configure:
   ```
   Framework Preset: Next.js
   Root Directory: frontend
   Build Command: next build
   Output Directory: .next
   ```
5. Add environment variables:
   ```env
   NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
   NEXT_PUBLIC_APP_NAME=AI Data Analyst
   ```
6. Click "Deploy"

#### Option B: Via Vercel CLI

```bash
# Navigate to frontend
cd frontend

# Login to Vercel
vercel login

# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

#### Vercel Configuration

Create `frontend/vercel.json`:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "env": {
    "NEXT_PUBLIC_API_URL": "@api-url"
  },
  "regions": ["iad1"],
  "crons": []
}
```

#### Update API Base URL

Update `frontend/services/api.ts` to use environment variable:

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = {
  login: `${API_BASE_URL}/api/v1/auth/login`,
  register: `${API_BASE_URL}/api/v1/auth/register`,
  datasets: `${API_BASE_URL}/api/v1/datasets`,
  chat: `${API_BASE_URL}/api/v1/chat`,
  visualize: `${API_BASE_URL}/api/v1/visualize`,
};
```

### Step 4: AI/LLM Setup (Groq)

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up for free account
3. Create API key:
   - Click "Create API Key"
   - Name: "ai-data-analyst"
   - Copy the key starting with `gsk_`
4. Add to Railway environment variables:
   ```
   GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxx
   ```

**Groq Free Tier**: Includes generous free usage for development and small production apps.

---

## Environment Variables Reference

### Backend (Railway)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | ✅ Yes | PostgreSQL connection string |
| `GROQ_API_KEY` | ✅ Yes | Groq API key for AI features |
| `SECRET_KEY` | ✅ Yes | JWT secret (32+ chars) |
| `OPENAI_API_KEY` | ❌ Optional | For enhanced AI features |
| `PYTHON_VERSION` | ❌ Optional | Default: 3.11 |
| `PORT` | ❌ Optional | Railway sets this automatically |

### Frontend (Vercel)

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | ✅ Yes | Backend URL (e.g., https://your-app.railway.app) |
| `NEXT_PUBLIC_APP_NAME` | ❌ Optional | App name for UI |

---

## Deployment Checklist

### Before Deploying

- [ ] Clean up local database: `rm backend/ai_analytics.db`
- [ ] Test locally with PostgreSQL connection string
- [ ] Update `.env` with production values
- [ ] Push all changes to GitHub
- [ ] Verify `requirements.txt` has all dependencies

### After Deploying

- [ ] Test health endpoint: `https://your-backend.railway.app/`
- [ ] Test API docs: `https://your-backend.railway.app/docs`
- [ ] Test login/register flow
- [ ] Test dataset upload
- [ ] Verify database tables created
- [ ] Test AI chat functionality
- [ ] Set up custom domain (optional)

---

## Troubleshooting

### Backend Issues

#### "ModuleNotFoundError: No module named 'psycopg2'"
- Ensure `psycopg2-binary` is in `requirements.txt`
- Rebuild on Railway (Settings → Redeploy)

#### "connection refused" to database
- Check DATABASE_URL format
- Ensure PostgreSQL is accepting connections
- Verify SSL mode: add `?sslmode=require`

#### "GROQ_API_KEY not found"
- Add variable in Railway dashboard
- Redeploy after adding

#### "Database does not exist"
- Create database in Neon console
- Check connection string is correct

### Frontend Issues

#### "Failed to fetch" from API
- Check `NEXT_PUBLIC_API_URL` is correct
- Verify CORS settings in backend
- Check backend is running

#### Build errors
- Check Node.js version (use 18.x or 20.x)
- Ensure all dependencies in `package.json`

---

## Alternative Deployment Options

### Option 1: All-in-One (Render.com)

**Pros**: Single platform, simple setup  
**Cons**: Cold starts can be slow

```bash
# 1. Create account at render.com
# 2. Connect GitHub repo
# 3. Create PostgreSQL database
# 4. Create Web Service for backend
# 5. Create Static Site for frontend
```

### Option 2: Docker (Self-Hosted)

**Pros**: Full control, no vendor lock-in  
**Cons**: Requires server management

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Deploy with:
```bash
docker build -t ai-data-analyst .
docker run -p 8000:8000 -e DATABASE_URL="..." ai-data-analyst
```

### Option 3: Coolify (Self-Hosted Free)

**Pros**: Free, all services on one server  
**Cons**: Requires VPS/server

1. Get a VPS (Hetzner, DigitalOcean, Linode)
2. Install Coolify
3. Connect GitHub repo
4. Deploy backend and frontend
5. Add PostgreSQL service

---

## Cost Estimation (Free Tier)

| Service | Free Tier | Monthly Cost |
|---------|-----------|--------------|
| Neon PostgreSQL | 10 GB storage | $0 |
| Railway | 500 hours/month | $0 |
| Vercel | 100 GB bandwidth | $0 |
| Groq | Generous free tier | $0 |
| **Total** | | **$0/month** |

> Note: Free tiers are sufficient for development and small production apps. Monitor usage as you scale.

---

## Security Best Practices

1. **Never commit `.env` files**
   - Add to `.gitignore`:
   ```
   .env
   *.env
   ```

2. **Use strong secrets**
   ```bash
   # Generate secure secret
   openssl rand -base64 32
   ```

3. **Enable SSL/TLS**
   - Neon: Use `?sslmode=require`
   - Railway: Automatic HTTPS
   - Vercel: Automatic HTTPS

4. **Rate limiting** (add to `main.py`):
   ```python
   from slowapi import Limiter, _rate_limit_exceeded_handler
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
   
   @app.post("/api/v1/chat")
   @limiter.limit("10/minute")
   async def chat(request: AskRequest, ...):
       ...
   ```

---

## Monitoring & Logs

### Backend Logs (Railway)
- View in Railway dashboard → Deployments → Logs
- Or use Railway CLI: `railway logs`

### Frontend Analytics (Vercel)
- Built-in Vercel Analytics
- Check dashboard for errors

### Database Monitoring (Neon)
- View query stats in Neon console
- Monitor connection limits
- Check storage usage

---

## Scaling Guide

### When Free Tier Isn't Enough

1. **Neon**: Upgrade compute size ($19+/month)
2. **Railway**: Upgrade plan ($5+/month)
3. **Vercel**: Pro plan ($20/month)
4. **Groq**: Pay as you go

### Performance Tips

- Add connection pooling to `database.py`
- Use Redis for caching (Upstash free tier)
- Implement database indexes
- Add CDN for static assets

---

## Support & Resources

- **Backend API Docs**: `https://your-backend.railway.app/docs`
- **GitHub Issues**: Report bugs here
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Next.js Docs**: https://nextjs.org/docs
- **Railway Docs**: https://docs.railway.app
- **Vercel Docs**: https://vercel.com/docs
- **Neon Docs**: https://neon.tech/docs
- **Groq Docs**: https://console.groq.com/docs

---

## Quick Commands Reference

```bash
# Local development
cd backend && uvicorn main:app --reload
cd frontend && npm run dev

# Deploy backend
railway up

# Deploy frontend
cd frontend && vercel --prod

# View logs
railway logs

# Check environment
railway variables

# Restart service
railway redeploy

# Database migrations (if needed)
alembic upgrade head
```

---

**Last Updated**: 2024
**Version**: 1.0.0

