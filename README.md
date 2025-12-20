#  Hirify - AI-Powered Resume and Job Matching Platform

<div align="center">


**Intelligent resume parsing and job matching system powered by advanced NLP and machine learning**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)

[📖 Documentation](./project.md) • [🔧 Installation](#-quick-start) • [📊 API Docs](#-api-documentation) • [🤝 Contributing](#-contributing)

</div>

---

##  Table of Contents

- [✨ Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [🛠️ Tech Stack](#️-tech-stack)
- [🚀 Quick Start](#-quick-start)
- [📊 API Documentation](#-api-documentation)
- [🧠 NLP Pipeline](#-nlp-pipeline)
- [📁 Project Structure](#-project-structure)
- [🔧 Configuration](#-configuration)
- [🚢 Deployment](#-deployment)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## ✨ Features

### 🎯 **Core Capabilities**
- **📄 Resume Processing**: Extract structured data from PDF, DOC, and DOCX files
- **🔍 Intelligent Matching**: Advanced NLP-powered job-candidate matching with similarity scoring
- **📊 Analytics Dashboard**: Comprehensive insights and performance metrics
- **⚡ Bulk Processing**: Handle multiple resumes and job descriptions simultaneously
- **🔄 Background Tasks**: Asynchronous processing with Celery and Redis

### 🧠 **AI & NLP Features**
- **Skills Extraction**: Intelligent identification and categorization of technical and soft skills
- **Semantic Analysis**: TF-IDF, cosine similarity, and BERT embeddings
- **Entity Recognition**: Automated extraction of contact info, experience, and education
- **Job Scraping**: Automated collection from multiple job boards
- **Match Explanations**: Detailed reasoning behind matching scores

### 💻 **User Experience**
- **Modern UI**: React 18 with TypeScript and Tailwind CSS
- **Real-time Updates**: Live status tracking and notifications
- **Drag & Drop**: Intuitive file upload interface
- **Export Options**: Multiple formats (CSV, Excel, PDF)
- **Mobile Responsive**: Optimized for all devices

---

## 🏗️ Architecture

```mermaid
graph TB
    A[React Frontend] --> B[FastAPI Backend]
    B --> C[PostgreSQL Database]
    B --> D[Redis Cache]
    B --> E[Celery Workers]
    E --> F[NLP Processing]
    F --> G[spaCy + NLTK + BERT]
    B --> H[Document Parser]
    H --> I[PDF/DOC/DOCX Files]
```

---

## 🛠️ Tech Stack

### **Frontend**
- **React 18** with TypeScript for type safety
- **Tailwind CSS** for modern, responsive design
- **Framer Motion** for smooth animations
- **React Query** for server state management
- **Vite** for fast development and building
- **shadcn/ui** for beautiful, accessible components

### **Backend**
- **FastAPI** (Python 3.11) for high-performance APIs
- **SQLAlchemy** ORM with PostgreSQL database
- **Celery** with Redis for background task processing
- **JWT Authentication** with bcrypt password hashing
- **Alembic** for database migrations

### **AI/ML & NLP**
- **spaCy** for advanced NLP processing
- **NLTK** for text preprocessing
- **scikit-learn** for machine learning algorithms
- **Transformers** (Hugging Face) for BERT embeddings
- **PDFPlumber** and **python-docx** for document parsing

### **DevOps & Infrastructure**
- **PostgreSQL** for reliable data storage
- **Redis** for caching and message brokering
- **Uvicorn** ASGI server for production
- **GitHub Actions** for CI/CD

---

## 🚀 Quick Start

### **Prerequisites**
- Python 3.11+
- Node.js 18+
- PostgreSQL 13+
- Redis 6+
- Git

### **💻 Local Development Setup**

#### **Backend Setup**
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Set up environment
cp .env.example .env

# Make sure PostgreSQL and Redis are running on your system
# PostgreSQL: localhost:5432
# Redis: localhost:6379

# Run database migrations
alembic upgrade head

# Start FastAPI server
uvicorn main:app --reload
```

#### **Frontend Setup**
```bash
# In a new terminal
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

#### **Background Tasks (Optional)**
```bash
# In another terminal
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
celery -A celery_app worker --loglevel=info
```

### ** Verify Installation**

| Service | URL | Status |
|---------|-----|--------|
| Frontend | http://localhost:3000 | ✅ Available |
| Backend API | http://localhost:8000 | ✅ Available |
| API Docs | http://localhost:8000/docs | ✅ Interactive |
| Health Check | http://localhost:8000/health | ✅ Monitoring |

---

## 📊 API Documentation

### **🔗 Interactive Documentation**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### **🛣️ Key Endpoints**

#### **Resume Management**
```http
POST   /api/v1/resumes/upload          # Upload resume
GET    /api/v1/resumes/                # List all resumes
GET    /api/v1/resumes/{id}            # Get specific resume
DELETE /api/v1/resumes/{id}            # Delete resume
POST   /api/v1/resumes/bulk-upload     # Bulk upload
```

#### **Job Management**
```http
POST   /api/v1/jobs/                   # Create job posting
GET    /api/v1/jobs/                   # List all jobs
PUT    /api/v1/jobs/{id}               # Update job
POST   /api/v1/jobs/scrape             # Scrape from job boards
```

#### **Matching Engine**
```http
POST   /api/v1/matching/match          # Create match
GET    /api/v1/matching/               # List matches
POST   /api/v1/matching/bulk-match     # Bulk matching
GET    /api/v1/matching/stats          # Match statistics
```

---

## 🧠 NLP Pipeline

### **📝 Document Processing Flow**
```
Resume Upload → Validation → Text Extraction → NLP Processing → Structured Data → Matching
```

### **🔍 Skills Extraction**
```python
# Multi-method skills extraction
skills_extractor = SkillsExtractor()
extracted_skills = skills_extractor.extract_skills(text)

# Categories: Technical, Soft Skills, Certifications, Tools
```

### **🎯 Matching Algorithm**
```python
# Weighted scoring system
scoring_weights = {
    'skills': 0.40,      # 40% - Technical skills match
    'experience': 0.30,  # 30% - Experience level
    'education': 0.20,   # 20% - Educational background
    'additional': 0.10   # 10% - Additional factors
}
```

---

## 📁 Project Structure

```
hirify/
├── 🖥️  backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/v1/endpoints/       # REST API routes
│   │   ├── core/                   # App configuration
│   │   ├── models/                 # Database models
│   │   ├── schemas/                # Pydantic schemas
│   │   ├── services/               # Business logic
│   │   └── tasks/                  # Celery background tasks
│   ├── alembic/                    # Database migrations
│   ├── tests/                      # Test suites
│   └── main.py                     # App entry point
├── ⚛️  frontend/                   # React frontend
│   ├── src/
│   │   ├── components/             # React components
│   │   ├── hooks/                  # Custom hooks
│   │   ├── services/               # API clients
│   │   └── types/                  # TypeScript definitions
│   └── public/                     # Static assets
├── 📋 .env.example                 # Environment template
└── 📖 README.md                    # This file
```

---

## 🔧 Configuration

### **📋 Environment Variables**
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/hirify

# Redis & Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=480

# File Upload
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_FILE_TYPES=pdf,doc,docx

# NLP Models
SPACY_MODEL=en_core_web_sm
SIMILARITY_THRESHOLD=0.5
```

### **🎛️ Performance Tuning**
- **Redis Caching**: Configurable TTL for different data types
- **Database Connection Pooling**: Optimized for concurrent requests
- **Background Processing**: Separate queues for different task priorities
- **File Storage**: Configurable upload directory and size limits

---

## 🚢 Deployment

### **🖥️ Production Deployment**
```bash
# Set production environment variables
export DATABASE_URL=postgresql://user:pass@localhost:5432/hirify
export SECRET_KEY=your-production-secret-key
export REDIS_URL=redis://localhost:6379/0

# Start the application
uvicorn main:app --host 0.0.0.0 --port 8000

# Health check
curl http://localhost:8000/health
```


### **🔍 Monitoring & Logging**
- Structured JSON logging with custom formatters
- Health checks for all services
- Performance metrics collection
- Error tracking and alerting

---


## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### **🛠️ Development Process**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### **📋 Code Standards**
- **Python**: Follow PEP 8, use type hints
- **TypeScript**: Strict mode enabled
- **Testing**: Maintain >80% test coverage
- **Documentation**: Update docs for new features

---

## 📞 Support & Community

- **📚 Documentation**: [Full Project Documentation](./project.md)
- **🐛 Bug Reports**: [GitHub Issues](https://github.com/yourusername/hirify/issues)
- **💡 Feature Requests**: [GitHub Discussions](https://github.com/yourusername/hirify/discussions)
- **📧 Contact**: [x](https://x.com/adnankhaan_ai)

---

## 🗺️ Roadmap

- [ ] **Enhanced NLP**: Custom training for domain-specific matching
- [ ] **Multi-language Support**: Process resumes in multiple languages
- [ ] **Advanced Analytics**: Machine learning insights and predictions
- [ ] **Mobile App**: Native mobile applications
- [ ] **API Rate Limiting**: Advanced throttling and quotas
- [ ] **Real-time Notifications**: WebSocket-based updates
- [ ] **Integration Hub**: Connect with popular ATS systems

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **spaCy** team for excellent NLP libraries
- **FastAPI** for the amazing web framework
- **React** community for frontend innovations
- **Hugging Face** for transformer models
- All contributors who help make Hirify better

---

<div align="center">

**⭐ Star this repo if you find it helpful!**

Made with ❤️ by the Hirify team

</div>

## 🆘 Support

For support, please open an issue in the GitHub repository or contact the development team.


