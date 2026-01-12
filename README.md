# ATS Web Application - Setup & Run Guide

AI-powered Applicant Tracking System (Proof of Concept)

## Architecture Overview

- **Backend**: Python FastAPI with ThreadPoolExecutor for async job processing
- **Frontend**: React + Vite + ShadCN UI components
- **Database**: SQL Server with vector similarity search
- **AI**: Ollama LLM for resume parsing and candidate matching

---

## Prerequisites

1. **Python 3.11+** with required packages (see `requirements.txt`)
2. **Node.js 20+** and npm
3. **SQL Server 2025** with the `ATSCohort` database
4. **Ollama** running on `http://localhost:11434` with:
   - `mistral` model for LLM operations
   - `nomic-embed-text` model for embeddings

---

## Step 1: Database Setup

Run the SQL script to create the Jobs table:

```sql
-- Execute in SQL Server Management Studio
USE ATSCohort;
GO

-- Run the script from: WebServer/schema/01_create_jobs_table.sql
```

---

## Step 2: Backend Setup

### Install Python Dependencies

```bash
cd <root folder>
pip install -r requirements.txt
```

### Update requirements.txt (if needed)

Ensure `requirements.txt` includes:
```
ollama
rapidfuzz
pydantic
typing_extensions
python-multipart
requests
uvicorn
fastapi
python-dotenv
pandas
numpy
python-dateutil
math
```

### Start the FastAPI Backend

```bash
cd multistage/WebServer
python main.py
```

The API will be available at: `http://localhost:8000`

API Endpoints:
- `POST /jobs/candidate` - Submit resume processing job
- `POST /jobs/employer` - Submit job matching job
- `GET /jobs/{job_id}` - Get job status and results

---

## Step 3: Frontend Setup

### Install Node Dependencies

```bash
cd multistage/WebServer/frontend
npm install
```

### Start the Vite Dev Server

```bash
npm run dev
```

The frontend will be available at: `http://localhost:5173`

---

## Usage

### 1. Process a Candidate Resume

1. Navigate to `http://localhost:5173`
2. Click "Process Candidate Resume"
3. Upload a PDF resume
4. Wait for AI processing (progress shown in real-time)
5. View extracted profile with identity, roles, and skills

### 2. Match Candidates to Job Description

1. Navigate to `http://localhost:5173`
2. Click "Match Candidates to Job"
3. Paste a job description (or use the sample)
4. Wait for AI matching (progress shown in real-time)
5. View ranked candidates with match scores and matched skills

---

## Project Structure

```
wwwroot/
├── multistage/
│   ├── Candidate/          # Resume processing logic
│   ├── Employer/           # Candidate matching logic
│   ├── Shared/             # Database & utilities
│   └── WebServer/
│       ├── main.py         # FastAPI application
│       ├── models.py       # Pydantic models
│       ├── database.py     # Job repository
│       ├── job_executor.py # Background job processor
│       ├── schema/         # SQL scripts
│       └── frontend/       # React application
│           ├── src/
│           │   ├── pages/      # Page components
│           │   ├── components/ # UI components
│           │   ├── hooks/      # Custom hooks
│           │   ├── lib/        # API & utilities
│           │   └── types/      # TypeScript types
│           ├── package.json
│           └── vite.config.ts
└── requirements.txt
```

---

## Troubleshooting

### Ollama Connection Issues

```bash
# Check Ollama is running
ollama list

# Pull required models
ollama pull mistral
ollama pull nomic-embed-text
```

### Database Connection Issues

Verify SQL Server is running and the connection string in `Shared/db.py`:
```python
SQL_CONFIG = {
    'server': 'Anvaya-Ryzen5\\SQLEXPRESS_2025',
    'database': 'ATSCohort',
    'driver': '{ODBC Driver 18 for SQL Server}'
}
```

### Frontend Proxy Issues

If API calls fail, verify `vite.config.ts` proxy configuration:
```js
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api/, ''),
  },
}
```

---

## Production Build (Future)

To build the frontend for production:

```bash
cd frontend
npm run build
```

The built files will be in `frontend/dist/`. Update `main.py` to serve these static files.
