# 🤖 AI Data Analyst

An intelligent data analytics platform powered by AI that automatically cleans datasets, generates visualizations, and answers natural language queries about your data.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![Next.js](https://img.shields.io/badge/Next.js-14.0+-black.svg)
![LangChain](https://img.shields.io/badge/LangChain-0.3.22-orange.svg)

## ✨ Features

- 🧹 **Intelligent Data Cleaning**
  - Automatic detection of data quality issues
  - Smart missing value imputation
  - Outlier detection and correction
  - Text-to-number conversion ("twenty-one" → 21)
  - Email validation and standardization
  - Date format normalization

- 📊 **Smart Visualizations**
  - Auto-generated charts based on data type
  - Interactive dashboards with KPI cards
  - Multiple chart types (bar, pie, line, scatter)
  - Real-time data filtering

- 💬 **Natural Language Queries**
  - Ask questions in plain English
  - AI-powered SQL generation
  - Context-aware responses
  - Chart recommendations

- 🔐 **Secure & Multi-tenant**
  - JWT-based authentication
  - User data isolation
  - Role-based access control

## 🏗️ Architecture

┌─────────────────┐ ┌──────────────────┐ ┌─────────────────┐
│ Next.js UI │◄────►│ FastAPI API │◄────►│ SQLite/PG DB │
│ (Frontend) │ │ (Backend) │ │ (Storage) │
└─────────────────┘ └──────────────────┘ └─────────────────┘
│
▼
┌──────────────────┐
│ LangChain Agent │
│ + Groq LLM │
│ + FAISS RAG │
└──────────────────┘

text

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- Groq API Key ([Get one free](https://console.groq.com/))

### Backend Setup

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-data-analyst.git
cd ai-data-analyst/backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# 5. Run the backend
uvicorn main:app --reload
Backend runs at: http://localhost:8000

Frontend Setup
bash
# 1. Navigate to frontend directory
cd ../frontend

# 2. Install dependencies
npm install
# or
yarn install

# 3. Set up environment variables
cp .env.example .env.local

# 4. Run the frontend
npm run dev
# or
yarn dev
Frontend runs at: http://localhost:3000

📚 API Documentation
Once running, visit:

Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc

🔑 Environment Variables
Backend (backend/.env)
text
GROQ_API_KEY=gsk_...              # Your Groq API key
SECRET_KEY=your-secret-key         # JWT secret
DATABASE_URL=sqlite:///./database.db
Frontend (frontend/.env.local)
text
NEXT_PUBLIC_API_URL=http://localhost:8000
📖 Usage Guide
1. Register/Login
Create an account or sign in to access the platform.

2. Upload Dataset
Click "Upload Dataset"

Select a CSV file

System automatically analyzes data quality

3. Clean Your Data
If issues are detected:

Click "Clean Dataset"

Review cleaning preview

Apply automated fixes

4. Query Your Data
Ask questions like:

"Show me a pie chart by vendor"

"What's the average price?"

"Compare sales by category"

5. Visualize Results
View auto-generated:

Interactive charts

KPI cards

Data tables with filters

🛠️ Tech Stack
Backend
Technology	Purpose
FastAPI	Web framework
LangChain 0.3.x	Agent orchestration
Groq (Llama 3.3 70B)	LLM inference
FAISS	Vector search
Sentence Transformers	Embeddings
Pandas	Data processing
SQLAlchemy	ORM
Frontend
Technology	Purpose
Next.js 14	React framework
Tailwind CSS	Styling
Recharts	Visualizations
Axios	HTTP client
Lucide Icons	Icons
📂 Project Structure
text
ai-data-analyst/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── agent.py                # LangChain agent logic
│   ├── data_cleaner.py         # Data cleaning algorithms
│   ├── auth.py                 # Authentication & JWT
│   ├── models.py               # Database models
│   ├── database.py             # DB connection
│   ├── rag.py                  # RAG implementation
│   ├── sql_tool.py             # Safe SQL execution
│   ├── chart_agent.py          # Chart recommendations
│   ├── requirements.txt        # Python dependencies
│   └── .env                    # Environment variables
│
├── frontend/
│   ├── app/                    # Next.js app directory
│   ├── components/             # React components
│   │   ├── DataCleaningModal.tsx
│   │   ├── DatasetTable.tsx
│   │   └── ChatInterface.tsx
│   ├── services/               # API services
│   ├── package.json            # Node dependencies
│   └── .env.local              # Frontend env vars
│
├── .gitignore
└── README.md
🧪 Testing
Backend Tests
bash
cd backend
pytest
Frontend Tests
bash
cd frontend
npm test
🚢 Deployment
Backend (Railway/Render/Fly.io)
Set environment variables

Deploy from GitHub

Add PostgreSQL addon

Update DATABASE_URL

Frontend (Vercel/Netlify)
Connect GitHub repository

Set NEXT_PUBLIC_API_URL

Deploy automatically on push

🤝 Contributing
Contributions are welcome! Please:

Fork the repository

Create a feature branch (git checkout -b feature/amazing-feature)

Commit changes (git commit -m 'Add amazing feature')

Push to branch (git push origin feature/amazing-feature)

Open a Pull Request

📝 License
This project is licensed under the MIT License - see LICENSE file.

🙏 Acknowledgments
LangChain for agent framework

Groq for blazing-fast LLM inference

FastAPI for the amazing web framework

Next.js for the React framework

📧 Contact
Raj Shekhar Singh - @rajshekhar

Project Link: https://github.com/YOUR_USERNAME/ai-data-analyst

🐛 Known Issues
SQLite may lock on concurrent writes (use PostgreSQL for production)

Large datasets (>10MB) may take longer to process

Groq API has rate limits on free tier

🗺️ Roadmap
 Support for Excel files

 Advanced statistical analysis

 Export reports as PDF

 Real-time collaboration

 More chart types

 SQL query builder UI

 Data versioning

Made with ❤️ using FastAPI, Next.js, and LangChain
