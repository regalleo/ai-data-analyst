# 🤖 AI Data Analyst

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![Next.js](https://img.shields.io/badge/Next.js-14.0+-black.svg)
![LangChain](https://img.shields.io/badge/LangChain-0.3.22-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**An intelligent data analytics platform powered by AI that automatically cleans datasets, generates visualizations, and answers natural language queries about your data.**

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-api-documentation) • [Usage Guide](#-usage-guide) • [Contributing](#-contributing)

</div>

---

## ✨ Features

### 🧹 Intelligent Data Cleaning

- **Automatic Quality Detection** - Identifies missing values, outliers, and inconsistencies
- **Smart Imputation** - Uses statistical methods to fill missing data intelligently
- **Outlier Management** - Detects and corrects statistical anomalies
- **Text Normalization** - Converts written numbers to digits ("twenty-one" → 21)
- **Email Validation** - Standardizes and validates email formats
- **Date Standardization** - Normalizes various date formats automatically

### 📊 Smart Visualizations

- **Auto-Generated Charts** - Automatically selects optimal chart types based on data
- **Interactive Dashboards** - Dynamic KPI cards with real-time updates
- **Multiple Chart Types** - Bar, pie, line, scatter, and more
- **Real-Time Filtering** - Filter and drill down into your data instantly

### 💬 Natural Language Queries

- **Plain English Questions** - No SQL knowledge required
- **AI-Powered SQL Generation** - Translates natural language to optimized queries
- **Context-Aware Responses** - Understands follow-up questions and context
- **Smart Recommendations** - Suggests relevant charts and analyses

### 🔐 Enterprise-Grade Security

- **JWT Authentication** - Secure token-based authentication
- **Multi-Tenant Architecture** - Complete data isolation between users
- **Role-Based Access Control** - Fine-grained permissions management
- **Secure API Endpoints** - All endpoints protected with authentication

---

## 🏗️ Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   Next.js UI    │◄────►│   FastAPI API    │◄────►│  SQLite/PG DB   │
│   (Frontend)    │      │    (Backend)     │      │   (Storage)     │
└─────────────────┘      └──────────────────┘      └─────────────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  LangChain Agent │
                         │   + Groq LLM     │
                         │   + FAISS RAG    │
                         └──────────────────┘
```

### Key Components

- **Frontend**: Next.js 14 with React Server Components
- **Backend**: FastAPI with async support
- **AI Engine**: LangChain agents powered by Groq's Llama 3.3 70B
- **Vector Store**: FAISS for semantic search and RAG
- **Database**: SQLite for development, PostgreSQL for production

---

## 🚀 Quick Start

### Prerequisites

Ensure you have the following installed:

- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **Groq API Key** ([Get free key](https://console.groq.com/))

### Backend Setup

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-data-analyst.git
cd ai-data-analyst/backend

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# 5. Initialize the database
python -c "from database import init_db; init_db()"

# 6. Run the backend server
uvicorn main:app --reload
```

✅ **Backend is now running at:** `http://localhost:8000`

### Frontend Setup

```bash
# 1. Navigate to frontend directory
cd ../frontend

# 2. Install dependencies
npm install
# or
yarn install

# 3. Set up environment variables
cp .env.example .env.local
# Edit .env.local if needed

# 4. Run the development server
npm run dev
# or
yarn dev
```

✅ **Frontend is now running at:** `http://localhost:3000`

---

## 📚 API Documentation

Interactive API documentation is available once the backend is running:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/register` | POST | Register new user |
| `/auth/login` | POST | Login and get JWT token |
| `/datasets/upload` | POST | Upload CSV dataset |
| `/datasets/{id}/analyze` | GET | Analyze data quality |
| `/datasets/{id}/clean` | POST | Clean dataset |
| `/datasets/{id}/query` | POST | Natural language query |
| `/datasets/{id}/visualize` | GET | Get visualizations |

---

## 🔑 Environment Variables

### Backend Configuration

Create a `.env` file in the `backend/` directory:

```env
# Required
GROQ_API_KEY=gsk_...              # Your Groq API key (required)
SECRET_KEY=your-secret-key-here   # JWT secret (generate with: openssl rand -hex 32)

# Database
DATABASE_URL=sqlite:///./database.db  # Use PostgreSQL in production

# Optional
DEBUG=True                        # Enable debug mode
LOG_LEVEL=INFO                    # Logging level
MAX_UPLOAD_SIZE=10485760          # Max file size (10MB)
```

### Frontend Configuration

Create a `.env.local` file in the `frontend/` directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=AI Data Analyst
```

---

## 📖 Usage Guide

### Step 1: Register/Login

- Navigate to `http://localhost:3000`
- Create a new account or sign in with existing credentials
- Receive JWT token for authenticated requests

### Step 2: Upload Dataset

- Click **"Upload Dataset"** button
- Select a CSV file (max 10MB)
- System automatically analyzes data quality
- View summary statistics and quality metrics

### Step 3: Clean Your Data

If data quality issues are detected:

- Click **"Clean Dataset"** button
- Review cleaning preview and recommendations
- Apply automated fixes with one click
- Download cleaned dataset if needed

### Step 4: Query Your Data

Ask questions in natural language:

- *"Show me a pie chart of sales by vendor"*
- *"What's the average price per category?"*
- *"Compare revenue across different regions"*
- *"Find the top 5 products by sales"*

### Step 5: Visualize Results

The system automatically generates:

- **Interactive Charts** - Bar, pie, line, scatter plots
- **KPI Cards** - Key metrics and statistics
- **Data Tables** - Filterable and sortable views
- **Export Options** - Download charts as PNG or data as CSV

---

## 🛠️ Tech Stack

### Backend Technologies

| Technology | Purpose | Version |
|------------|---------|---------|
| **FastAPI** | High-performance web framework | 0.104+ |
| **LangChain** | Agent orchestration & LLM workflows | 0.3.22 |
| **Groq** | Ultra-fast LLM inference (Llama 3.3 70B) | Latest |
| **FAISS** | Vector similarity search | Latest |
| **Sentence Transformers** | Text embeddings | Latest |
| **Pandas** | Data manipulation & analysis | Latest |
| **SQLAlchemy** | SQL toolkit & ORM | 2.0+ |
| **Pydantic** | Data validation | 2.0+ |
| **Python-Jose** | JWT token handling | Latest |

### Frontend Technologies

| Technology | Purpose | Version |
|------------|---------|---------|
| **Next.js** | React framework with SSR | 14.0+ |
| **React** | UI library | 18+ |
| **Tailwind CSS** | Utility-first CSS framework | 3.0+ |
| **Recharts** | Composable charting library | Latest |
| **Axios** | HTTP client | Latest |
| **Lucide React** | Icon library | Latest |
| **React Hook Form** | Form management | Latest |

---

## 📂 Project Structure

```
ai-data-analyst/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── agent.py                # LangChain agent orchestration
│   ├── data_cleaner.py         # Data cleaning algorithms
│   ├── auth.py                 # JWT authentication & authorization
│   ├── models.py               # SQLAlchemy database models
│   ├── database.py             # Database connection & initialization
│   ├── rag.py                  # RAG implementation with FAISS
│   ├── sql_tool.py             # Safe SQL query execution
│   ├── chart_agent.py          # Chart recommendation engine
│   ├── requirements.txt        # Python dependencies
│   └── .env                    # Environment variables (create from .env.example)
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx            # Home page
│   │   ├── login/              # Authentication pages
│   │   └── dashboard/          # Main dashboard
│   ├── components/
│   │   ├── DataCleaningModal.tsx    # Data cleaning UI
│   │   ├── DatasetTable.tsx         # Dataset display
│   │   ├── ChatInterface.tsx        # Query interface
│   │   └── Visualizations.tsx       # Chart components
│   ├── services/
│   │   └── api.ts              # API client
│   ├── package.json            # Node dependencies
│   └── .env.local              # Frontend environment variables
│
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_agent.py
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

---

## 🚢 Deployment

### Backend Deployment

#### Option 1: Railway

1. Create account at [Railway.app](https://railway.app)
2. Connect GitHub repository
3. Add PostgreSQL database from Railway marketplace
4. Set environment variables:
   - `GROQ_API_KEY`
   - `SECRET_KEY`
   - `DATABASE_URL` (auto-provided by Railway)
5. Deploy automatically on push to main branch

#### Option 2: Render

1. Create account at [Render.com](https://render.com)
2. Create new Web Service from GitHub repo
3. Select `backend` directory as root
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add PostgreSQL database
7. Set environment variables

#### Option 3: Fly.io

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login and launch
fly auth login
cd backend
fly launch

# Set secrets
fly secrets set GROQ_API_KEY=your_key_here
fly secrets set SECRET_KEY=your_secret_here

# Deploy
fly deploy
```

### Frontend Deployment

#### Option 1: Vercel (Recommended)

1. Create account at [Vercel.com](https://vercel.com)
2. Import your GitHub repository
3. Set root directory to `frontend`
4. Configure build settings:
   - Build Command: `npm run build`
   - Output Directory: `.next`
5. Add environment variable:
   - `NEXT_PUBLIC_API_URL` = your backend URL
6. Deploy automatically on every push

#### Option 2: Netlify

1. Create account at [Netlify.com](https://netlify.com)
2. Connect GitHub repository
3. Base directory: `frontend`
4. Build command: `npm run build`
5. Publish directory: `.next`
6. Add environment variables
7. Deploy

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Development Workflow

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/ai-data-analyst.git
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make your changes**
   - Write clean, documented code
   - Add tests for new features
   - Update documentation as needed

4. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```

5. **Push to your branch**
   ```bash
   git push origin feature/amazing-feature
   ```

6. **Open a Pull Request**
   - Describe your changes clearly
   - Reference any related issues
   - Wait for review and address feedback

### Code Style Guidelines

#### Python (Backend)
- Follow PEP 8 style guide
- Use Black formatter: `black .`
- Use type hints where possible
- Write docstrings for functions and classes

#### TypeScript (Frontend)
- Follow Airbnb style guide
- Use Prettier formatter: `npm run format`
- Use TypeScript strict mode
- Write meaningful component and variable names

#### Commit Messages
Follow conventional commits format:
- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation changes
- `style:` formatting, missing semicolons, etc.
- `refactor:` code restructuring
- `test:` adding tests
- `chore:` maintenance tasks

### Running Tests Before PR

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Linting
npm run lint
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Special thanks to the following projects and organizations:

- [LangChain](https://github.com/langchain-ai/langchain) - For the amazing agent framework
- [Groq](https://groq.com/) - For blazing-fast LLM inference
- [FastAPI](https://fastapi.tiangolo.com/) - For the excellent web framework
- [Next.js](https://nextjs.org/) - For the powerful React framework
- [Vercel](https://vercel.com/) - For hosting and deployment platform

---

## 📧 Contact

**Raj Shekhar Singh**

- GitHub: [@rajshekhar](https://github.com/rajshekhar)
- Email: rajshekhar@example.com
- Project Link: [https://github.com/YOUR_USERNAME/ai-data-analyst](https://github.com/YOUR_USERNAME/ai-data-analyst)

---

## 🐛 Known Issues

- **SQLite Concurrency**: SQLite may lock on concurrent writes. Use PostgreSQL for production environments.
- **Large Datasets**: Files larger than 10MB may take longer to process. Consider implementing chunking for very large datasets.
- **API Rate Limits**: Groq free tier has rate limits (60 requests/minute). Implement caching or upgrade to paid tier.
- **Chart Rendering**: Some complex chart types require specific data structures. Check documentation for requirements.

**Reporting Issues**: Please use the [GitHub Issues](https://github.com/YOUR_USERNAME/ai-data-analyst/issues) page with detailed reproduction steps.

---

## 🗺️ Roadmap

### Version 1.1 (Q1 2026)
- [ ] Support for Excel files (.xlsx, .xls)
- [ ] Advanced statistical analysis (correlation, regression)
- [ ] Export reports as PDF
- [ ] Data import from Google Sheets

### Version 1.2 (Q2 2026)
- [ ] Real-time collaboration features
- [ ] More chart types (heatmaps, treemaps, sankey diagrams)
- [ ] SQL query builder UI
- [ ] Scheduled data refreshes

### Version 2.0 (Q3 2026)
- [ ] Data versioning and history tracking
- [ ] Custom data transformations with Python
- [ ] API rate limiting and caching
- [ ] Multi-language support (i18n)
- [ ] Mobile app (React Native)

### Future Considerations
- [ ] Integration with BI tools (Tableau, Power BI)
- [ ] Machine learning model training
- [ ] Automated anomaly detection
- [ ] Custom dashboard builder

**Have a feature request?** Open an issue with the `enhancement` label!

---

## 📊 Project Stats

![GitHub stars](https://img.shields.io/github/stars/YOUR_USERNAME/ai-data-analyst?style=social)
![GitHub forks](https://img.shields.io/github/forks/YOUR_USERNAME/ai-data-analyst?style=social)
![GitHub issues](https://img.shields.io/github/issues/YOUR_USERNAME/ai-data-analyst)
![GitHub pull requests](https://img.shields.io/github/issues-pr/YOUR_USERNAME/ai-data-analyst)

---

## 💡 FAQ

### Q: Do I need a paid Groq account?
A: No, the free tier is sufficient for development and small-scale use. Upgrade for higher rate limits.

### Q: Can I use a different LLM provider?
A: Yes! The system is designed to be LLM-agnostic. Modify the `agent.py` file to use OpenAI, Anthropic, or other providers.

### Q: Is my data secure?
A: Yes. All data is stored in your own database with user isolation. We recommend using environment variables for sensitive data.

### Q: Can I deploy this for commercial use?
A: Yes, this project is MIT licensed. You're free to use it commercially.

### Q: What's the maximum dataset size?
A: Default limit is 10MB. You can adjust `MAX_UPLOAD_SIZE` in the backend configuration.

---

## 🎯 Performance Tips

1. **Use PostgreSQL in Production**: SQLite is great for development but PostgreSQL handles concurrency better
2. **Enable Caching**: Cache frequent queries to reduce LLM API calls
3. **Optimize Large Datasets**: Use pagination and lazy loading for tables with 10,000+ rows
4. **Index Database Columns**: Add indexes to frequently queried columns
5. **Use CDN for Frontend**: Deploy frontend assets to CDN for faster loading

---

<div align="center">

**Made with ❤️ using FastAPI, Next.js, and LangChain**

⭐ Star this repo if you find it helpful!

[Report Bug](https://github.com/YOUR_USERNAME/ai-data-analyst/issues) • [Request Feature](https://github.com/YOUR_USERNAME/ai-data-analyst/issues) • [Discussions](https://github.com/YOUR_USERNAME/ai-data-analyst/discussions)

</div>
