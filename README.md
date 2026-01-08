# AI Data Analyst - Setup Guide

## Manual Setup Steps to Get the App Running

### Step 1: Install PostgreSQL (if not installed)

**Option A: Using Homebrew (Recommended for Mac)**
```bash
# Install PostgreSQL
brew install postgresql@15

# Start PostgreSQL service
brew services start postgresql@15

# Add to PATH (add to ~/.zshrc or ~/.bash_profile)
echo 'export PATH="/usr/local/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Option B: Download from PostgreSQL.org**
- Download PostgreSQL 15+ from https://www.postgresql.org/download/
- Run the installer and follow instructions

### Step 2: Create Database and User

Open terminal and run:
```bash
# Switch to postgres user (if needed)
sudo -u postgres psql

# Or connect directly if you're admin
psql -U postgres

# In psql, run these commands:
CREATE DATABASE ai_analytics;
CREATE USER postgres WITH ENCRYPTED PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE ai_analytics TO postgres;
ALTER DATABASE ai_analytics OWNER TO postgres;

# Connect to the database
\c ai_analytics

# Grant schema permissions
GRANT ALL ON SCHEMA public TO postgres;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO postgres;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO postgres;

# Exit psql
\q
```

### Step 3: Install Python Dependencies

```bash
cd /Users/rajshekharsingh/Desktop/ai-data-analyst/backend
pip install -r requirements.txt
```

Or install individually:
```bash
pip install fastapi uvicorn pandas sqlalchemy psycopg2-binary python-multipart \
    langchain openai faiss-cpu rank-bm25 sentence-transformers matplotlib \
    pydantic python-jose passlib bcrypt PyJWT
```

### Step 4: Set Environment Variables (Optional but Recommended)

Create a `.env` file in `/Users/rajshekharsingh/Desktop/ai-data-analyst/backend/`:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_analytics
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your-super-secret-key-change-this
```

### Step 5: Start the Backend Server

```bash
cd /Users/rajshekharsingh/Desktop/ai-data-analyst/backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Step 6: Start the Frontend

Open a new terminal:
```bash
cd /Users/rajshekharsingh/Desktop/ai-data-analyst/frontend
npm run dev
```

### Step 7: Access the Application

- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## Troubleshooting PostgreSQL

### If PostgreSQL is not running:
```bash
# Check status
brew services list | grep postgresql

# Start it
brew services start postgresql@15

# Or if installed differently
pg_ctl -D /usr/local/var/postgresql@15 start
```

### If connection is refused:
```bash
# Check if PostgreSQL is listening
pg_isready -h localhost -p 5432

# Check pg_hba.conf (authentication settings)
```

### If database doesn't exist:
```bash
# Create it
createdb ai_analytics
```

### If you get "role does not exist":
```bash
# Create the role
createuser -s postgres
```

---

## Quick One-Line Setup (Run in Terminal)

```bash
# 1. Install PostgreSQL
brew install postgresql@15 2>/dev/null || echo "PostgreSQL may already be installed"

# 2. Start PostgreSQL
brew services start postgresql@15 2>/dev/null || pg_ctl -D /usr/local/var/postgresql@15 start

# 3. Create database and user (run this in psql)
# psql -U postgres -c "CREATE DATABASE ai_analytics;" \
#    -c "CREATE USER postgres WITH ENCRYPTED PASSWORD 'postgres';" \
#    -c "GRANT ALL PRIVILEGES ON DATABASE ai_analytics TO postgres;"

# 4. Install dependencies
cd /Users/rajshekharsingh/Desktop/ai-data-analyst/backend
pip install -q fastapi uvicorn pandas sqlalchemy psycopg2-binary python-multipart langchain openai faiss-cpu rank-bm25 sentence-transformers matplotlib pydantic python-jose passlib bcrypt PyJWT

# 5. Start backend
uvicorn main:app --host 0.0.0.0 --port 8000 &
```

---

## Environment Variables

Create `.env` file:
```
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_analytics

# Security
SECRET_KEY=your-secret-key-min-32-chars-long

# OpenAI (required for AI features)
OPENAI_API_KEY=sk-...
```

---

## Project Structure

```
ai-data-analyst/
├── backend/
│   ├── main.py           # FastAPI app entry point
│   ├── database.py       # DB connection
│   ├── models.py         # SQLAlchemy models
│   ├── auth.py           # JWT authentication
│   ├── agent.py          # LangChain agent
│   ├── sql_tool.py       # Safe SQL execution
│   ├── rag.py            # RAG index management
│   ├── hybrid_search.py  # BM25 + Vector search
│   ├── chart_agent.py    # Chart auto-selection
│   └── requirements.txt
└── frontend/
    ├── app/
    │   ├── page.tsx          # Landing page
    │   ├── login/page.tsx    # Login page
    │   ├── register/page.tsx # Register page
    │   └── dashboard/page.tsx # Main dashboard
    ├── components/
    │   ├── Chat.tsx          # Chat interface
    │   ├── UploadDataset.tsx # CSV upload
    │   └── ChartRenderer.tsx # Chart display
    ├── services/
    │   └── api.ts            # API client
    └── hooks/
        └── useAuth.tsx       # Auth hook
```

---

## Common Issues

1. **"ModuleNotFoundError: No module named 'psycopg2'"**
   - Run: `pip install psycopg2-binary`

2. **"connection refused"**
   - PostgreSQL not running: `brew services start postgresql@15`
   - Wrong port: Default is 5432

3. **"database does not exist"**
   - Run: `createdb ai_analytics`

4. **"role does not exist"**
   - Run: `createuser -s postgres`

5. **"passlib" or "bcrypt" not found**
   - Run: `pip install passlib bcrypt`

