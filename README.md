# AI-Powered Applicant Tracking System

An intelligent resume processing and candidate matching system that combines LLM-based extraction, vector similarity search, and multi-dimensional scoring to achieve 85%+ match accuracy.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)
- [Performance](#performance)
- [Architecture Documentation](#architecture-documentation)

---

## Overview

This ATS system processes unstructured PDF resumes into structured candidate profiles and matches them to job descriptions using:
- **Multi-stage skill normalization**: Exact → Alias → Token → Vector matching cascade
- **Role-specific weighting**: Different skill importance based on target role
- **Seniority-aware matching**: Junior/Mid/Senior/Lead experience tracking
- **Evidence-based scoring**: Full provenance for all skill claims
- **Eligibility gating**: Hard filters before scoring for efficiency

### Key Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Candidate Match Accuracy | 85%+ (manual eval) | High |
| Resume Processing Time | ~15 seconds | Fast |
| JD Matching Time | ~6 seconds | Fast |
| Concurrent Job Capacity | 2+ (scalable) | Good |

---

## Key Features

### Candidate Processing
- **Layout-Aware PDF Parsing**: Uses IBM Docling for intelligent document parsing
- **Identity Extraction**: Separate LLM call for contact info accuracy
- **Experience Inference**: Job title-based seniority detection
- **Duration Calculation**: Deterministic month calculation (no LLM hallucinations)
- **Skill Evidence Tracking**: Tracks where and how skills were discovered
- **Multi-Stage Matching**: Progressive fallback with disambiguation rules

### Employer Matching
- **Structured JD Parsing**: Extracts domain, seniority, and requirements
- **Category Requirements**: Supports "any of" matching (e.g., "React or Angular or Vue")
- **Eligibility Gate**: Filters out unqualified candidates before scoring
- **Role-Specific Weights**: Backend devs value Java more; frontend devs value React more
- **Seniority Thresholds**: Enforces minimum experience levels by career stage
- **Detailed Score Breakdown**: Per-skill contribution visualization

### Data Layer
- **Contextual Embeddings**: Skill + Domain + Role for accurate vectors
- **Embedding Cache**: DB-based cache with access tracking
- **Skill Hierarchy**: Parent-child relationships and skill implications
- **Disambiguation Rules**: Database-driven false positive prevention

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                         │
│                     http://localhost:5173                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       API Layer (FastAPI)                       │
│                     http://localhost:8000                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Job Queue                                 │
│                    (ThreadPoolExecutor)                         │
└───────────┬─────────────────────────────────────┬───────────────┘
            │                                     │
            ▼                                     ▼
┌──────────────────────┐              ┌──────────────────────┐
│ Candidate Pipeline   │              │ Employer Pipeline    │
│                      │              │                      │
│ 1. PDF Parsing       │              │ 1. JD Parsing        │
│ 2. LLM Extraction    │              │ 2. Eligibility Gate  │
│ 3. Duration Calc     │              │ 3. Scoring           │
│ 4. Skill Matching    │              │ 4. Normalization     │
│ 5. Vectorization     │              │ 5. Ranking           │
└──────────┬───────────┘              └──────────┬───────────┘
           │                                     │
           ▼                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                        AI Services                               │
│  • gpt-oss:20b-cloud (quick classifications)                   │
│  • qwen3-next:80b-cloud (complex reasoning)                    │
│  • nomic-embed-text (768-dim vectors)                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SQL Server 2025                              │
│  • MasterSkills (taxonomy + vectors)                            │
│  • CandidateSkills (evidence tracking)                          │
│  • RoleSkillTypeWeights (role-specific weights)                 │
│  • SkillImplications (skill relationships)                      │
│  • EmbeddingCache (performance optimization)                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Backend
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | FastAPI 0.115+ | Async API server |
| Runtime | Python 3.11+ | Business logic |
| Job Queue | ThreadPoolExecutor | Background processing |
| Database | SQL Server 2025 | Storage + vector search |
| PDF Parser | Docling | Document parsing |
| LLM (Fast) | gpt-oss:20b-cloud | Quick classifications |
| LLM (Thinking) | qwen3-next:80b-cloud | Complex reasoning |
| Embeddings | nomic-embed-text | Vector generation |

### Frontend
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | React 18.3+ | UI rendering |
| Build Tool | Vite 6.0+ | Fast development |
| Language | TypeScript 5.6+ | Type safety |
| UI Library | ShadCN UI | Accessible components |
| Styling | Tailwind CSS 3.4+ | Utility CSS |
| State | React hooks | Local state management |

---

## Prerequisites

1. **Python 3.11+** with pip
2. **Node.js 20+** and npm
3. **SQL Server 2025** with `ATSCohort` database
4. **Ollama** running on `http://localhost:11434` with:
   - `gpt-oss:20b-cloud` model for fast tasks
   - `qwen3-next:80b-cloud` model for complex reasoning
   - `nomic-embed-text` model for embeddings

---

## Installation

### Step 1: Database Setup

Run the SQL script to create all required tables:

```sql
-- Execute in SQL Server Management Studio
USE ATSCohort;
GO

-- Run the schema script from: multistage/WebServer/schema/db.sql
```

This creates tables for:
- Jobs (async orchestration)
- Candidates (registry)
- MasterSkills (enhanced taxonomy)
- CandidateSkills (evidence tracking)
- RoleSkillTypeWeights (role-specific weights)
- SkillImplications (skill relationships)
- EmbeddingCache (performance)
- And more...

### Step 2: Backend Setup

```bash
cd multistage/WebServer
pip install -r requirements.txt
```

**requirements.txt includes:**
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
pyodbc
docling
```

### Step 3: Frontend Setup

```bash
cd multistage/WebServer/frontend
npm install
```

### Step 4: Verify Ollama Models

```bash
# Check Ollama is running
ollama list

# Pull required models (if not already present)
ollama pull gpt-oss:20b-cloud
ollama pull qwen3-next:80b-cloud
ollama pull nomic-embed-text
```

---

## Usage

### Starting the Backend

```bash
cd multistage/WebServer
python main.py
```

The API will be available at: `http://localhost:8000`

### Starting the Frontend

```bash
cd multistage/WebServer/frontend
npm run dev
```

The frontend will be available at: `http://localhost:5173`

### Process a Candidate Resume

1. Navigate to `http://localhost:5173`
2. Click **"Process Candidate Resume"**
3. Upload a PDF resume
4. View real-time progress (text extraction → LLM parsing → skill matching)
5. See extracted profile with:
   - Identity (name, email, links)
   - Experience timeline with verified durations
   - Technologies and domains per role
   - Evidence sources for each skill

### Match Candidates to Job Description

1. Navigate to `http://localhost:5173`
2. Click **"Match Candidates to Job"**
3. Paste a job description (min 50 characters)
4. View real-time progress (JD parsing → eligibility filtering → scoring)
5. See ranked candidates with:
   - 0-100 match scores
   - Confidence labels (Strong/Good/Partial/Weak)
   - Per-skill contribution breakdown
   - Matched and unmatched skills

---

## Project Structure

```
wwwroot/
├── multistage/
│   ├── Candidate/              # Resume processing pipeline
│   │   ├── document_chunk_parser.py  # PDF parsing with Docling
│   │   ├── chunk_processor.py        # LLM extraction
│   │   ├── postprocessor.py          # Duration calc & skill processing
│   │   ├── vectorizer.py             # DB sync & evidence tracking
│   │   └── schemas/                  # Pydantic models
│   ├── Employer/               # Candidate matching engine
│   │   ├── MatchingEngine.py         # Core ranking logic
│   │   ├── PostProcessor.py          # JD post-processing
│   │   └── schemas/                  # LLM response models
│   ├── Shared/                 # Shared utilities
│   │   ├── db.py                     # Database connection
│   │   ├── normalizer.py             # Multi-stage skill matching
│   │   ├── ollama_service.py         # LLM service with retry
│   │   └── embedder.py               # Embedding generation
│   └── WebServer/              # FastAPI application
│       ├── main.py                   # FastAPI app
│       ├── models.py                 # Pydantic models
│       ├── database.py               # Job repository
│       ├── job_executor.py           # Background job processor
│       ├── schema/                   # SQL scripts
│       └── frontend/                 # React application
│           ├── src/
│           │   ├── pages/            # Page components
│           │   ├── components/       # UI components
│           │   ├── hooks/            # Custom hooks
│           │   ├── lib/              # API & utilities
│           │   └── types/            # TypeScript types
│           ├── package.json
│           └── vite.config.ts
├── architecture/             # Detailed architecture docs
│   ├── 00_system_overview.md
│   ├── 01_candidate_resume_processor_architecture.md
│   ├── 02_employer_matching_system_architecture.md
│   ├── 03_frontend_ui_architecture.md
│   └── my-thoughts.md
└── requirements.txt          # Python dependencies
```

---

## API Documentation

### Endpoints

| Method | Endpoint | Request | Response |
|--------|----------|---------|----------|
| POST | `/jobs/candidate` | `multipart/form-data` (PDF) | `{job_id: uuid}` |
| POST | `/jobs/employer` | `{job_description: string}` | `{job_id: uuid}` |
| GET | `/jobs/{job_id}` | - | Job object with status/results |

### Job Object Structure

```typescript
{
  id: string,              // UUID
  type: 'candidate' | 'employer',
  status: 'queued' | 'processing' | 'completed' | 'failed',
  progress: number,        // 0-100
  message: string,         // "Extracting text chunks"
  result?: {
    // Candidate result
    profile: {
      identity: {full_name, linkedin, github},
      candidate_roles: [{title, verified_duration, raw_technologies, domains}]
    }

    // OR Employer result
    matches: [{
      name: string,
      candidate_id: number,
      score: number,        // 0-100
      matches: string[],    // ["Java (verified)", "Docker (inferred)"]
      confidence: string,   // "Strong Match" | "Good Match" | ...
      skill_breakdown: [{   // Per-skill contribution
        skill_name: string,
        contribution_to_total: number,
        experience_months: number,
        competency_score: number,
        weight: number
      }]
    }],
    role_context: string | {primary_domain, seniority_level}
  },
  created_at: ISO8601,
  error_message?: string
}
```

---

## Troubleshooting

### Ollama Connection Issues

**Symptom**: `ConnectionError` or timeout when processing jobs

**Solution**:
```bash
# Check Ollama is running
ollama list

# Verify models are present
ollama pull gpt-oss:20b-cloud
ollama pull qwen3-next:80b-cloud
ollama pull nomic-embed-text

# Test connection
curl http://localhost:11434/api/tags
```

### Database Connection Issues

**Symptom**: `pyodbc.InterfaceError` or login failures

**Solution**: Verify connection string in `Shared/db.py`:
```python
SQL_CONFIG = {
    'server': 'YOUR_SERVER\\SQLEXPRESS_2025',
    'database': 'ATSCohort',
    'driver': '{ODBC Driver 18 for SQL Server}'
}
```

### Frontend Proxy Issues

**Symptom**: API calls fail with CORS or connection errors

**Solution**: Verify `vite.config.ts` proxy configuration:
```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api/, ''),
  },
}
```

### LLM JSON Extraction Errors

**Symptom**: `JSON decode error` in job logs

**Solution**: The OllamaService automatically retries with different prompts. If persistent:
1. Check model is loaded: `ollama list`
2. Try simpler job descriptions
3. Check Ollama logs: `docker logs ollama` (if running in Docker)

### Slow Processing

**Symptom**: Jobs take > 60 seconds

**Solution**:
1. Check embedding cache is being used (first run is slower)
2. Reduce concurrent jobs in `job_executor.py`
3. Verify SQL Server indexes are created (see `schema/db.sql`)

---

## Performance

### Candidate Processing Breakdown

| Stage | Time | Optimization |
|-------|------|--------------|
| PDF parsing (Docling) | ~2s | I/O bound |
| LLM header normalization | ~0.5s | Fast model |
| LLM identity extraction | ~1s | Dedicated call |
| LLM experience extraction | ~4s | Thinking model |
| Duration calculation | <0.1s | Python (deterministic) |
| Embedding generation | ~5s | Cached (first run) |
| Multi-stage skill matching | ~2s | Indexed queries |
| DB upsert | ~1s | Batch operations |
| **Total** | **~15s** | - |

### Employer Matching Breakdown

| Stage | Time | Optimization |
|-------|------|--------------|
| LLM JD parsing | ~3s | Thinking model |
| Load role weights | ~0.1s | Cached |
| Eligibility gate | ~1s | 80% reduction |
| Scoring eligible only | ~2s | Optimized queries |
| Normalization | <0.1s | Python |
| **Total** | **~6s** | - |

### Cache Performance

| Scenario | Without Cache | With Cache |
|----------|--------------|------------|
| First embedding lookup | ~500ms | ~500ms |
| Subsequent lookups | ~500ms each | ~10ms (DB query) |
| 100 lookups | 50 seconds | 0.5 seconds (99% reduction) |

---

## Architecture Documentation

For detailed architecture documentation, see the `architecture/` folder:

1. **[System Overview](./architecture/00_system_overview.md)** - Complete system architecture
2. **[Candidate Resume Processor](./architecture/01_candidate_resume_processor_architecture.md)** - Resume parsing & profile extraction
3. **[Employer Matching System](./architecture/02_employer_matching_system_architecture.md)** - JD parsing & candidate ranking
4. **[Frontend UI Architecture](./architecture/03_frontend_ui_architecture.md)** - React application design
5. **[Author's Thoughts](./architecture/my-thoughts.md)** - Design decisions & learnings

---

## License

This is a proof-of-concept project for educational purposes.

---

## Support

For issues or questions:
1. Check the [troubleshooting section](#troubleshooting)
2. Review the [architecture documentation](#architecture-documentation)
3. Check the database schema in `multistage/WebServer/schema/db.sql`
