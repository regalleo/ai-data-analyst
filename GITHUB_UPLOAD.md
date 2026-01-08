# AI Data Analyst - GitHub Upload Guide

This guide covers uploading your AI Data Analyst app to GitHub.

---

## Prerequisites

1. **GitHub Account**: https://github.com (sign up if needed)
2. **Git Installed**: Check with `git --version`
3. **GitHub CLI** (optional but recommended): `brew install gh`

---

## Step 1: Create GitHub Repository

### Option A: Via GitHub Website

1. Go to https://github.com/new
2. Repository name: `ai-data-analyst`
3. Description: `AI-powered data analytics platform with chat interface`
4. Set to **Public** or **Private**
5. **Do NOT** initialize with README (we have one)
6. Click "Create repository"

### Option B: Via GitHub CLI

```bash
# Authenticate (if first time)
gh auth login

# Create repository
gh repo create ai-data-analyst --public --description "AI-powered data analytics platform"

# Or with interactive prompts
gh repo create
```

---

## Step 2: Prepare Local Repository

### Initialize Git (if not already done)

```bash
cd /Users/rajshekharsingh/Desktop/ai-data-analyst

# Initialize git repo
git init

# Create main branch
git branch -M main
```

### Configure Git (first time only)

```bash
# Set your name
git config user.name "Your Name"

# Set your email (use email associated with GitHub)
git config user.email "your-email@example.com"
```

---

## Step 3: Add and Commit Files

### Check Status
```bash
git status
```

### Add All Files
```bash
# Add all files (respects .gitignore)
git add .
```

### Create Commit
```bash
git commit -m "Initial commit: AI Data Analyst app

Features:
- FastAPI backend with JWT authentication
- Next.js 14 frontend with TypeScript
- PostgreSQL/SQLite database support
- LangChain + Groq AI integration
- Hybrid search (BM25 + Vector)
- Data cleaning and visualization
- Deployment configurations for Render, Railway, Vercel"
```

---

## Step 4: Connect to GitHub

### Add Remote (if created on GitHub)
```bash
git remote add origin https://github.com/YOUR-USERNAME/ai-data-analyst.git
```

### Verify Remote
```bash
git remote -v
# Should show:
# origin  https://github.com/YOUR-USERNAME/ai-data-analyst.git (fetch)
# origin  https://github.com/YOUR-USERNAME/ai-data-analyst.git (push)
```

---

## Step 5: Push to GitHub

```bash
# Push main branch
git push -u origin main
```

**Enter your credentials when prompted:**
- Username: Your GitHub username
- Password: Your GitHub password (or Personal Access Token)

> **Note**: If using 2FA, you need a Personal Access Token instead of password.
> Generate one at: https://github.com/settings/tokens

---

## Step 6: Verify Upload

1. Go to https://github.com/YOUR-USERNAME/ai-data-analyst
2. Check that all files are present:
   ```
   ai-data-analyst/
   ├── README.md
   ├── DEPLOYMENT.md
   ├── DEPLOYMENT_CHECKLIST.md
   ├── RENDER_DEPLOYMENT.md
   ├── TODO.md
   ├── .gitignore
   └── backend/
       ├── main.py
       ├── database.py
       ├── models.py
       ├── auth.py
       ├── agent.py
       └── ...
   └── frontend/
       ├── app/
       ├── components/
       └── ...
   ```

---

## Using GitHub CLI (Faster Method)

If you have GitHub CLI installed:

```bash
# Navigate to project
cd /Users/rajshekharsingh/Desktop/ai-data-analyst

# Initialize and push in one command
gh repo create ai-data-analyst --public --source=. --push

# Or interactive mode
gh repo create
```

---

## Git Commands Reference

### Daily Workflow

```bash
# Check status
git status

# Add changes
git add .

# Commit
git commit -m "Description of changes"

# Push to GitHub
git push origin main

# Pull latest changes
git pull origin main
```

### Undo Mistakes

```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo and discard changes
git reset --hard HEAD~1

# Revert a specific file
git checkout -- filename.py
```

### Create Branches

```bash
# Create new branch
git checkout -b feature/new-feature

# Switch to branch
git checkout main

# Merge branch
git merge feature/new-feature

# Delete branch
git branch -d feature/new-feature
```

---

## Setting Up GitHub Integration

### For Deployment Platforms

After uploading to GitHub, you can connect:

| Platform | Setup |
|----------|-------|
| **Render** | Deploy → Connect GitHub repo |
| **Railway** | Deploy → Connect GitHub repo |
| **Vercel** | Add Project → Import from GitHub |
| **Neon** | No GitHub integration needed |

---

## Best Practices

### 1. Use .gitignore
Your `.gitignore` should exclude:
```
.env           # Secrets
*.db           # Local database
node_modules/  # Dependencies
.next/         # Build output
__pycache__/   # Python cache
```

### 2. Use Branches
```bash
# Create branch for changes
git checkout -b fix/login-bug

# Make changes, commit, push
git add .
git commit -m "Fix login bug"
git push -u origin fix/login-bug

# Create Pull Request on GitHub
```

### 3. Write Good Commits
```
# Good commit messages:
- "Fix: Login redirect issue"
- "Feat: Add data export functionality"
- "Docs: Update deployment guide"
- "Refactor: Clean up authentication code"

# Avoid:
- "Fixed stuff"
- "Updated"
- "WIP"
```

### 4. Tag Releases
```bash
# Create a tag
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push tag
git push origin v1.0.0
```

---

## Troubleshooting

### "remote origin already exists"
```bash
# Remove existing remote
git remote remove origin

# Add again
git remote add origin https://github.com/YOUR-USERNAME/ai-data-analyst.git
```

### "Authentication failed"
- Use Personal Access Token instead of password
- Generate at: https://github.com/settings/tokens

### "Everything up-to-date" but files not on GitHub
```bash
# Check if remote is set correctly
git remote -v

# Force push (careful!)
git push -u origin main --force
```

### Large files rejected
```bash
# Install Git LFS
brew install git-lfs

# Track large files
git lfs track "*.csv"
git lfs track "*.model"

# Commit tracking file
git add .gitattributes
git commit -m "Add LFS tracking"
```

---

## Quick Upload Commands

Run this sequence to upload your project:

```bash
cd /Users/rajshekharsingh/Desktop/ai-data-analyst

# 1. Initialize
git init
git branch -M main

# 2. Configure
git config user.name "Your Name"
git config user.email "your-email@example.com"

# 3. Add and commit
git add .
git commit -m "Initial commit: AI Data Analyst with FastAPI, Next.js, LangChain"

# 4. Create repo and push
gh repo create ai-data-analyst --public --source=. --push
```

---

## After Upload

1. ✅ Verify files on GitHub
2. ✅ Add topics: `fastapi`, `nextjs`, `ai`, `data-analytics`
3. ✅ Update README with deployment status
4. ✅ Enable GitHub Pages (optional, for docs)

---

## Resources

- [Git Handbook](https://docs.github.com/en/get-started/using-git)
- [GitHub CLI](https://cli.github.com)
- [Git LFS](https://git-lfs.github.com)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)

---

**Last Updated**: 2024
**Version**: 1.0.0

