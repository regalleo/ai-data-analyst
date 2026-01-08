# AI Data Analyst - Deployment Checklist

## Pre-Deployment Checklist

### 1. Code Preparation
- [ ] All code committed to GitHub
- [ ] `requirements.txt` updated with all dependencies
- [ ] `package.json` verified with all dependencies
- [ ] `.gitignore` includes `.env` files
- [ ] No hardcoded API keys or secrets in code

### 2. Local Testing
- [ ] Backend runs: `cd backend && uvicorn main:app --reload`
- [ ] Frontend runs: `cd frontend && npm run dev`
- [ ] Login/Register works
- [ ] Dataset upload works
- [ ] AI chat works
- [ ] Charts render correctly

### 3. Database Setup (Neon)
- [ ] Created Neon account
- [ ] Created new project
- [ ] Created database `ai_analytics`
- [ ] Copied connection string with `?sslmode=require`
- [ ] Ran schema.sql in Neon console

### 4. Environment Variables

#### Backend (Railway)
| Variable | Value | Set |
|----------|-------|-----|
| `DATABASE_URL` | postgresql://... | [ ] |
| `GROQ_API_KEY` | gsk_... | [ ] |
| `SECRET_KEY` | 32+ char string | [ ] |
| `OPENAI_API_KEY` | sk-... (optional) | [ ] |

#### Frontend (Vercel)
| Variable | Value | Set |
|----------|-------|-----|
| `NEXT_PUBLIC_API_URL` | https://backend.railway.app | [ ] |

---

## Deployment Steps

### Step 1: Deploy Backend to Railway
- [ ] Log in to [Railway.app](https://railway.app)
- [ ] Click "New Project" → "Deploy from GitHub"
- [ ] Select repository
- [ ] Set root directory: `backend`
- [ ] Add environment variables
- [ ] Click "Deploy"
- [ ] Wait for deployment to complete
- [ ] Copy backend URL (e.g., `https://your-app.railway.app`)

### Step 2: Verify Backend
- [ ] Health check: `https://your-app.railway.app/`
- [ ] API docs: `https://your-app.railway.app/docs`
- [ ] Test login endpoint with curl:
  ```bash
  curl -X POST https://your-app.railway.app/api/v1/auth/register \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"test123"}'
  ```

### Step 3: Deploy Frontend to Vercel
- [ ] Log in to [Vercel.com](https://vercel.com)
- [ ] Click "Add New..." → "Project"
- [ ] Import GitHub repository
- [ ] Set root directory: `frontend`
- [ ] Add `NEXT_PUBLIC_API_URL` with backend URL
- [ ] Click "Deploy"

### Step 4: Verify Frontend
- [ ] Visit deployed URL
- [ ] Check browser console for errors
- [ ] Verify API calls work
- [ ] Test complete user flow

---

## Post-Deployment Checklist

### 1. Functionality Tests
- [ ] User registration works
- [ ] User login works
- [ ] Logout works
- [ ] Dataset upload works
- [ ] Data cleaning works
- [ ] AI chat responds correctly
- [ ] Charts display properly
- [ ] KPI cards show data
- [ ] Download cleaned data works

### 2. Security Checks
- [ ] JWT tokens work
- [ ] User can only see their own data
- [ ] Invalid tokens are rejected
- [ ] SQL injection protection works
- [ ] File upload validation works

### 3. Performance Checks
- [ ] Page load time < 3 seconds
- [ ] API response time < 2 seconds
- [ ] Chat responses < 10 seconds
- [ ] No memory leaks visible

### 4. Error Handling
- [ ] Invalid login shows error
- [ ] Missing files show error
- [ ] API errors handled gracefully
- [ ] Network errors show user-friendly messages

---

## Rollback Plan

### If Something Goes Wrong:

1. **Backend Issues**:
   - Go to Railway Dashboard → Deployments
   - Click "Rollback" on previous working deployment
   - Or fix code and redeploy

2. **Frontend Issues**:
   - Go to Vercel Dashboard → Deployments
   - Click "Rollback" on previous working deployment
   - Or fix code and redeploy

3. **Database Issues**:
   - Neon has automatic backups
   - Contact Neon support if needed
   - Restore from backup if necessary

4. **Complete Rollback**:
   ```bash
   # Revert Git
   git revert <commit-hash>
   git push origin main
   ```

---

## Monitoring & Maintenance

### Regular Checks
- [ ] Check Railway logs weekly
- [ ] Monitor Vercel analytics
- [ ] Check Neon database usage
- [ ] Review Groq API usage

### Alerts to Set Up
- [ ] Railway deployment failure notifications
- [ ] Vercel error rate alerts
- [ ] Neon storage limit warnings
- [ ] Groq API quota notifications

---

## Cost Tracking

| Service | Free Tier Limit | Current Usage | Status |
|---------|-----------------|---------------|--------|
| Neon | 10 GB storage | ___ GB | ✅ OK |
| Railway | 500 hours/month | ___ hours | ✅ OK |
| Vercel | 100 GB bandwidth | ___ GB | ✅ OK |
| Groq | Free tier | ___ % used | ✅ OK |

---

## Useful Commands

### Local Development
```bash
# Start backend
cd backend && uvicorn main:app --reload

# Start frontend
cd frontend && npm run dev

# Test API
curl http://localhost:8000/

# Check logs
tail -f backend/backend.log
```

### Railway CLI
```bash
# Install
curl -fsSL https://railway.app/install.sh | sh

# Login
railway login

# View logs
railway logs

# Set variable
railway variables set GROQ_API_KEY="..."

# Redeploy
railway redeploy

# Check status
railway status
```

### Vercel CLI
```bash
# Install
npm i -g vercel

# Login
vercel login

# Deploy preview
vercel

# Deploy production
vercel --prod

# View logs
vercel logs
```

---

## Resources

### Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Next.js Docs](https://nextjs.org/docs)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org)
- [LangChain Docs](https://python.langchain.com)

### Platform Docs
- [Railway Docs](https://docs.railway.app)
- [Vercel Docs](https://vercel.com/docs)
- [Neon Docs](https://neon.tech/docs)
- [Groq Docs](https://console.groq.com/docs)

### Support
- GitHub Issues: Report bugs
- Railway Discord: Deployment help
- Vercel Community: Frontend questions
- Stack Overflow: General programming questions

---

## Version History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2024 | 1.0.0 | Initial deployment guide | AI Data Analyst |

