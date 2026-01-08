# AI Data Analyst - Deployment Tasks

## Deployment Status: 📋 NOT STARTED

---

## 📋 Pre-Deployment Tasks

### 1. Code & Repository
- [ ] Ensure all code is committed to GitHub
- [ ] Create GitHub repo if not exists
- [ ] Verify `requirements.txt` has all dependencies
- [ ] Verify `package.json` has all dependencies
- [ ] Check `.gitignore` excludes `.env` files

### 2. Local Testing
- [ ] Test backend: `cd backend && uvicorn main:app --reload`
- [ ] Test frontend: `cd frontend && npm run dev`
- [ ] Verify login/register flow
- [ ] Verify dataset upload
- [ ] Verify AI chat functionality
- [ ] Verify charts render

---

## 🚀 Deployment Tasks

### Database (Neon PostgreSQL)
- [ ] Create Neon account: https://neon.tech
- [ ] Create new project (`ai-analyst-prod`)
- [ ] Create database `ai_analytics`
- [ ] Copy connection string with `?sslmode=require`
- [ ] Run `backend/schema.sql` in Neon console

### Backend (Railway)
- [ ] Create Railway account: https://railway.app
- [ ] Deploy from GitHub repo (root: `backend`)
- [ ] Add environment variables:
  - [ ] `DATABASE_URL`
  - [ ] `GROQ_API_KEY`
  - [ ] `SECRET_KEY`
- [ ] Verify deployment successful
- [ ] Copy backend URL (e.g., `https://xxx.railway.app`)

### Frontend (Vercel)
- [ ] Create Vercel account: https://vercel.com
- [ ] Deploy from GitHub repo (root: `frontend`)
- [ ] Add environment variable:
  - [ ] `NEXT_PUBLIC_API_URL` = backend URL
- [ ] Verify deployment successful

### AI Setup (Groq)
- [ ] Create Groq account: https://console.groq.com
- [ ] Generate API key
- [ ] Add to Railway environment variables

---

## ✅ Post-Deployment Verification

### Functionality Tests
- [ ] Frontend loads correctly
- [ ] User registration works
- [ ] User login works
- [ ] Dataset upload works
- [ ] AI chat responds correctly
- [ ] Charts display properly
- [ ] KPI cards show data
- [ ] Download cleaned data works

### Security Tests
- [ ] JWT authentication works
- [ ] Users see only their own data
- [ ] Invalid tokens rejected

### Performance Tests
- [ ] Page load < 3 seconds
- [ ] API response < 2 seconds
- [ ] Chat response < 10 seconds

---

## 🎯 Quick Deploy Commands

```bash
# 1. Test locally first
cd backend && uvicorn main:app --reload &
cd frontend && npm run dev

# 2. Deploy backend to Railway
railway login
railway init
railway variables set DATABASE_URL="postgresql://..."
railway variables set GROQ_API_KEY="gsk_..."
railway up

# 3. Deploy frontend to Vercel
cd frontend
vercel login
vercel --prod
```

---

## 📞 Resources

| Service | URL | Purpose |
|---------|-----|---------|
| Neon | https://neon.tech | Free PostgreSQL |
| Railway | https://railway.app | Backend hosting |
| Vercel | https://vercel.com | Frontend hosting |
| Groq | https://console.groq.com | AI/LLM API |

---

## 📝 Notes

- Free tiers available for all services
- Total cost: $0/month for small apps
- Monitor usage as you scale
- See DEPLOYMENT.md for detailed guide
- See DEPLOYMENT_CHECKLIST.md for complete checklist

