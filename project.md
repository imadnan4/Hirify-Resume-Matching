# Hirify - AI-Powered Resume and Job Matching Platform - Comprehensive Project Documentation

This is an intelligent resume parsing and job matching system that leverages advanced Natural Language Processing (NLP) techniques to match job candidates with opportunities. The system uses machine learning, semantic analysis, and sophisticated algorithms to provide accurate matching scores.

## 🚀 Project Overview

Hirify is a full-stack application that:
- Parses resumes from PDF, DOC, and DOCX files
- Extracts structured data (skills, experience, education)
- Matches candidates with job descriptions
- Provides detailed scoring and analytics
- Supports bulk processing and background tasks

## 🛠️ Technology Stack

### Frontend Technologies
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS for responsive design
- **Animations**: Framer Motion for smooth interactions
- **State Management**: React Query for server state
- **HTTP Client**: Axios for API communication
- **Routing**: React Router v6
- **Build Tool**: Vite (fast development server)
- **UI Components**: Radix UI primitives with shadcn/ui
- **Form Handling**: React Hook Form with Zod validation
- **Charts**: Recharts for data visualization

### Backend Technologies
- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migration**: Alembic for database versioning
- **Task Queue**: Celery with Redis broker
- **Caching**: Redis for high-performance caching
- **Authentication**: JWT tokens with bcrypt hashing
- **NLP Libraries**: 
  - spaCy for advanced NLP processing
  - NLTK for text preprocessing
  - scikit-learn for machine learning
  - Transformers (Hugging Face) for BERT embeddings
- **Document Processing**: 
  - PDFPlumber for PDF parsing
  - python-docx for Word documents
  - PyPDF2 for backup PDF handling
- **Web Scraping**: Beautiful Soup 4 and Selenium
- **Validation**: Pydantic for data validation
- **Testing**: pytest with asyncio support

### DevOps & Deployment
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Docker Compose
- **Process Management**: Uvicorn ASGI server
- **Environment Management**: Python venv
- **Version Control**: Git with .gitignore

## 📁 Detailed Project Structure

```
hirify/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── api/               # API layer
│   │   │   └── v1/
│   │   │       └── endpoints/ # Route handlers
│   │   │           ├── resumes.py      # Resume CRUD operations
│   │   │           ├── jobs.py         # Job management
│   │   │           ├── matching.py     # Matching algorithms
│   │   │           ├── auth.py         # Authentication
│   │   │           └── candidates.py   # Candidate profiles
│   │   ├── core/              # Core application setup
│   │   │   ├── config.py      # Configuration settings
│   │   │   ├── database.py    # Database connection
│   │   │   └── logging_config.py # Logging setup
│   │   ├── models/            # SQLAlchemy database models
│   │   │   ├── resume.py      # Resume model
│   │   │   ├── job_description.py # Job model
│   │   │   ├── match.py       # Match results model
│   │   │   ├── candidate.py   # Candidate profiles
│   │   │   ├── user.py        # User authentication
│   │   │   └── skill.py       # Skills taxonomy
│   │   ├── schemas/           # Pydantic schemas for validation
│   │   │   ├── resume.py      # Resume request/response schemas
│   │   │   ├── job.py         # Job schemas
│   │   │   ├── match.py       # Matching schemas
│   │   │   └── auth.py        # Authentication schemas
│   │   ├── services/          # Business logic services
│   │   │   ├── document_parser.py     # Main document coordinator
│   │   │   ├── pdf_parser.py          # PDF extraction
│   │   │   ├── docx_parser.py         # Word document extraction
│   │   │   ├── resume_parser.py       # Resume structure extraction
│   │   │   ├── skills_extractor.py    # Skills identification
│   │   │   ├── matching_service.py    # Matching algorithms
│   │   │   ├── similarity_engine.py   # Semantic similarity
│   │   │   ├── job_scraper.py         # Job board scraping
│   │   │   ├── nlp_advanced.py        # Advanced NLP processing
│   │   │   ├── cache_service.py       # Redis caching
│   │   │   ├── auth_service.py        # Authentication logic
│   │   │   └── export_service.py      # Data export functionality
│   │   └── tasks/             # Celery background tasks
│   │       ├── resume_tasks.py        # Resume processing tasks
│   │       ├── job_tasks.py           # Job scraping tasks
│   │       ├── matching_tasks.py      # Matching computation
│   │       └── monitoring_tasks.py    # System monitoring
│   ├── alembic/              # Database migrations
│   ├── uploads/              # File upload storage
│   ├── logs/                 # Application logs
│   ├── tests/                # Test suites
│   ├── main.py               # FastAPI app entry point
│   ├── celery_app.py         # Celery configuration
│   ├── requirements.txt      # Python dependencies
│   ├── alembic.ini          # Migration configuration
│   └── Dockerfile           # Container configuration
├── frontend/                 # React TypeScript frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── Dashboard.tsx         # Main dashboard
│   │   │   ├── ResumeManager.tsx     # Resume upload/management
│   │   │   ├── JobManager.tsx        # Job creation/management
│   │   │   ├── MatchingInterface.tsx # Matching interface
│   │   │   ├── Analytics.tsx         # Analytics dashboard
│   │   │   ├── Layout.tsx           # App layout wrapper
│   │   │   └── ui/                  # Reusable UI components
│   │   ├── services/         # API integration
│   │   │   └── api.ts               # API client with TypeScript
│   │   ├── hooks/            # Custom React hooks
│   │   ├── utils/            # Utility functions
│   │   ├── types/            # TypeScript type definitions
│   │   └── styles/           # Global styles
│   ├── public/               # Static assets
│   ├── package.json          # Node.js dependencies
│   ├── tsconfig.json         # TypeScript configuration
│   ├── tailwind.config.js    # Tailwind CSS configuration
│   ├── vite.config.ts        # Vite build configuration
│   └── Dockerfile           # Container configuration
├── docs/                    # Documentation
├── scripts/                 # Utility scripts
├── nginx/                   # Nginx configuration
├── .github/                 # GitHub Actions workflows
├── docker-compose.yml       # Development environment
├── docker-compose.prod.yml  # Production environment
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore patterns
├── README.md               # Project overview
└── project.md              # This comprehensive documentation
```

## 🔄 Application Workflow

### 1. Resume Upload & Processing
```
User uploads resume → File validation → Save to storage → 
Create database record → Queue background processing → 
Extract text → Parse structure → Extract skills/experience → 
Store structured data → Update status
```

### 2. Job Description Management
```
User creates job OR scrapes from job boards → 
Validate job data → Extract requirements → 
Identify required skills → Store in database → 
Make available for matching
```

### 3. Matching Process
```
User initiates matching → Load resume and job data → 
Calculate similarity scores → Apply weighted scoring → 
Generate match explanations → Store results → 
Display ranked matches
```

### 4. Background Processing
```
Celery worker picks up task → Process heavy NLP operations → 
Update progress in Redis → Complete task → 
Notify frontend of completion
```

## 📊 Database Schema

### Core Tables

#### Resumes Table
```sql
CREATE TABLE resumes (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_type VARCHAR(10),
    file_size INTEGER,
    upload_date TIMESTAMP DEFAULT NOW(),
    processed_date TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending',
    extracted_text TEXT,
    structured_data JSON,
    processing_errors JSON,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Job Descriptions Table
```sql
CREATE TABLE job_descriptions (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    requirements TEXT,
    location VARCHAR(255),
    salary_range VARCHAR(100),
    employment_type VARCHAR(50),
    experience_level VARCHAR(50),
    source VARCHAR(100),
    source_url TEXT,
    extracted_skills JSON,
    structured_data JSON,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Matches Table
```sql
CREATE TABLE matches (
    id SERIAL PRIMARY KEY,
    resume_id INTEGER REFERENCES resumes(id),
    job_id INTEGER REFERENCES job_descriptions(id),
    overall_score FLOAT NOT NULL,
    skills_score FLOAT,
    experience_score FLOAT,
    education_score FLOAT,
    matched_skills JSON,
    missing_skills JSON,
    skill_overlap_count INTEGER DEFAULT 0,
    total_required_skills INTEGER DEFAULT 0,
    explanation JSON,
    confidence_level VARCHAR(20),
    recommendation TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(resume_id, job_id)
);
```

## 🛣️ API Endpoints

### Resume Management
- **POST** `/api/v1/resumes/upload` - Upload single resume
- **POST** `/api/v1/resumes/bulk-upload` - Upload multiple resumes
- **GET** `/api/v1/resumes/` - List all resumes with pagination
- **GET** `/api/v1/resumes/{id}` - Get specific resume
- **PUT** `/api/v1/resumes/{id}` - Update resume
- **DELETE** `/api/v1/resumes/{id}` - Delete resume
- **GET** `/api/v1/resumes/{id}/status` - Check processing status
- **POST** `/api/v1/resumes/{id}/reprocess` - Reprocess resume

### Job Management
- **POST** `/api/v1/jobs/` - Create new job
- **GET** `/api/v1/jobs/` - List all jobs with filtering
- **GET** `/api/v1/jobs/{id}` - Get specific job
- **PUT** `/api/v1/jobs/{id}` - Update job
- **DELETE** `/api/v1/jobs/{id}` - Delete job
- **POST** `/api/v1/jobs/scrape` - Scrape jobs from URLs
- **GET** `/api/v1/jobs/search/skills` - Search jobs by skills
- **GET** `/api/v1/jobs/{id}/skills` - Get extracted skills

### Matching Engine
- **POST** `/api/v1/matching/match` - Create single match
- **POST** `/api/v1/matching/bulk-match` - Bulk matching
- **GET** `/api/v1/matching/` - List matches with filtering
- **GET** `/api/v1/matching/{id}` - Get specific match
- **PUT** `/api/v1/matching/{id}` - Update match
- **DELETE** `/api/v1/matching/{id}` - Delete match
- **GET** `/api/v1/matching/{id}/explanation` - Get match explanation
- **GET** `/api/v1/matching/stats` - Get matching statistics
- **GET** `/api/v1/matching/top-matches` - Get top matches

### Authentication
- **POST** `/api/v1/auth/login` - User login
- **POST** `/api/v1/auth/register` - User registration
- **POST** `/api/v1/auth/refresh` - Refresh access token
- **POST** `/api/v1/auth/logout` - User logout
- **POST** `/api/v1/auth/forgot-password` - Password reset request
- **POST** `/api/v1/auth/reset-password` - Reset password

## 🧠 NLP Processing Pipeline

### 1. Document Parsing
```python
# Document validation
validator = DocumentValidator()
validation_result = validator.validate_file(file_path, filename)

# Text extraction based on file type
if file_type == 'pdf':
    text = pdf_parser.extract_text(file_path)
elif file_type in ['doc', 'docx']:
    text = docx_parser.extract_text(file_path)

# Text cleaning and preprocessing
clean_text = preprocessor.clean_text(text)
```

### 2. Information Extraction
```python
# Skills extraction using multiple methods
skills_extractor = SkillsExtractor()
extracted_skills = skills_extractor.extract_skills(text)

# Experience extraction
experience_data = resume_parser.extract_experience(text)

# Education extraction
education_data = resume_parser.extract_education(text)

# Contact information extraction
contact_info = resume_parser.extract_contact_info(text)
```

### 3. Semantic Analysis
```python
# Use spaCy for advanced NLP
import spacy
nlp = spacy.load('en_core_web_sm')
doc = nlp(text)

# Extract entities
entities = [(ent.text, ent.label_) for ent in doc.ents]

# Calculate semantic similarity
similarity_score = doc1.similarity(doc2)
```

### 4. Matching Algorithm
```python
# Weighted scoring system
scoring_weights = {
    'skills': 0.40,      # 40% weight
    'experience': 0.30,  # 30% weight
    'education': 0.20,   # 20% weight
    'additional': 0.10   # 10% weight
}

# Calculate overall match score
overall_score = (
    skills_score * scoring_weights['skills'] +
    experience_score * scoring_weights['experience'] +
    education_score * scoring_weights['education'] +
    additional_score * scoring_weights['additional']
)
```

## 🎯 Frontend Components

### Dashboard Component
- Overview statistics
- Recent activity
- Quick actions
- Performance metrics

### Resume Manager
- Drag & drop file upload
- Processing status tracking
- Resume preview
- Bulk operations

### Job Manager
- Job creation form
- Job listing with filters
- Job scraping interface
- Requirements extraction

### Matching Interface
- Single vs bulk matching
- Match results visualization
- Detailed scoring breakdown
- Export functionality

### Analytics Dashboard
- Match statistics
- Performance charts
- Trend analysis
- Success metrics

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/resume_parser

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=480

# File Upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_FILE_TYPES=pdf,doc,docx

# NLP Models
SPACY_MODEL=en_core_web_sm
BERT_MODEL=bert-base-uncased
SIMILARITY_THRESHOLD=0.5

# Performance
ENABLE_CACHING=true
CACHE_TTL=3600
```

## 🚀 How to Run the Project

### Using Docker (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd hirify

# Copy environment variables
cp .env.example .env

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Local Development
```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Run migrations
alembic upgrade head

# Start FastAPI server
uvicorn main:app --reload

# In another terminal - start Celery worker
celery -A celery_app worker --loglevel=info

# Frontend setup (in another terminal)
cd frontend
npm install
npm run dev
```

## 📈 Performance Optimizations

### Caching Strategy
- Redis caching for frequently accessed data
- Application-level caching for expensive NLP operations
- Database query result caching
- File processing result caching

### Background Processing
- Celery workers for heavy NLP tasks
- Task queues for different priority levels
- Progress tracking for long-running operations
- Automatic retry mechanisms for failed tasks

### Database Optimizations
- Proper indexing on frequently queried columns
- Connection pooling for better performance
- Pagination for large result sets
- Query optimization for complex joins

## 🔐 Security Features

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (RBAC)
- Password hashing with bcrypt
- Session management
- Password reset functionality

### Data Protection
- Input validation with Pydantic
- SQL injection prevention
- XSS protection
- CSRF protection
- File upload security

### API Security
- Rate limiting
- CORS configuration
- Request/response logging
- Error handling without information leakage

## 📝 Testing

### Backend Tests
```bash
cd backend
pytest --cov=app tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 🚢 Deployment

### Production Setup
```bash
# Build and deploy with Docker
docker-compose -f docker-compose.prod.yml up -d

# Or deploy to cloud platforms:
# - AWS ECS/EKS
# - Google Cloud Run/GKE
# - Azure Container Instances/AKS
# - DigitalOcean App Platform
```

### Monitoring & Logging
- Application logs with structured logging
- Performance monitoring
- Error tracking
- Health checks for all services
- Metrics collection

## 🎯 Key Features

### Resume Processing
- Support for PDF, DOC, and DOCX files
- Advanced text extraction with error handling
- Structured data extraction (skills, experience, education)
- Bulk processing capabilities
- Processing status tracking

### Job Matching
- Intelligent matching algorithm with weighted scoring
- Semantic similarity using NLP models
- Detailed match explanations
- Confidence levels and recommendations
- Bulk matching operations

### Analytics
- Match statistics and performance metrics
- Success rate tracking
- Trend analysis
- Export capabilities (CSV, Excel, PDF)

### User Interface
- Modern responsive design
- Real-time updates
- Drag & drop file uploads
- Interactive charts and visualizations
- Mobile-friendly interface

## 🔄 Data Flow

1. **File Upload**: User uploads resume → Validation → Storage
2. **Processing**: Background task → Text extraction → Data parsing
3. **Matching**: User initiates match → Algorithm calculation → Score generation
4. **Results**: Match display → Analytics → Export options

## 🎨 UI/UX Features

- **Dashboard**: Overview of system performance and recent activity
- **Resume Manager**: Intuitive file upload and management interface
- **Job Manager**: Easy job creation and management tools
- **Matching Interface**: Visual matching results with detailed breakdowns
- **Analytics**: Comprehensive reporting and data visualization

## 📊 Monitoring & Observability

### Health Checks
- Database connectivity
- Redis availability
- Celery worker status
- API endpoint health

### Metrics
- Processing times
- Success/failure rates
- Resource utilization
- User activity

### Logging
- Structured JSON logging
- Error tracking
- Performance monitoring
- Security event logging

This comprehensive documentation provides everything needed to understand, develop, deploy, and maintain the Resume Parser system. The project is designed to be scalable, maintainable, and production-ready.

## 🚀 Quick Start - Step by Step Guide

### Prerequisites
- Python 3.11+ installed
- Node.js 18+ installed
- PostgreSQL installed (or use Docker)
- Redis installed (or use Docker)

### Step 1: Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download spaCy model**
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Set up environment variables**
   ```bash
   # Copy the environment file
   cp .env.example .env
   
   # Edit .env file with your database credentials if needed
   ```

6. **Start database services (if using Docker)**
   ```bash
   # Start PostgreSQL and Redis
   docker-compose up -d postgres redis
   ```

7. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

8. **Start FastAPI backend server**
   ```bash
   uvicorn main:app --reload
   ```
   
   The backend will be available at: http://localhost:8000
   API documentation at: http://localhost:8000/docs

### Step 2: Frontend Setup

1. **Open a new terminal and navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```
   
   The frontend will be available at: http://localhost:5173

### Step 3: Optional - Start Celery Worker (for background tasks)

1. **Open another terminal and navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Activate virtual environment**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Start Celery worker**
   ```bash
   celery -A celery_app worker --loglevel=info
   ```

### 🎉 You're Ready!

Now you can:
- Access the frontend at http://localhost:5173
- Access the backend API at http://localhost:8000
- View API documentation at http://localhost:8000/docs
- Upload resumes and create job descriptions
- Run matching algorithms
- View analytics and results

### 📝 Summary of Running Services

| Service | URL | Status |
|---------|-----|--------|
| Frontend (React) | http://localhost:5173 | ✅ Running |
| Backend (FastAPI) | http://localhost:8000 | ✅ Running |
| API Docs | http://localhost:8000/docs | ✅ Available |
| Database | localhost:5432 | ✅ Running |
| Redis | localhost:6379 | ✅ Running |
| Celery Worker | Background | ✅ Optional |

### 🔧 Troubleshooting

**If you encounter issues:**

1. **Database connection errors:**
   - Make sure PostgreSQL is running
   - Check your DATABASE_URL in .env file
   - Verify database credentials

2. **Redis connection errors:**
   - Make sure Redis is running
   - Check REDIS_URL in .env file

3. **Module import errors:**
   - Make sure virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

4. **Frontend build errors:**
   - Delete node_modules and reinstall: `rm -rf node_modules && npm install`
   - Check Node.js version compatibility

5. **Port conflicts:**
   - Change ports in configuration files if needed
   - Backend: modify uvicorn command `--port 8001`
   - Frontend: modify vite.config.ts

### 🎯 Development Tips

- Keep the virtual environment activated while working on backend
- Use `--reload` flag with uvicorn for auto-restart on code changes
- Monitor logs in all terminals to debug issues
- Use the API documentation at /docs to test endpoints
- Check the browser console for frontend errors
