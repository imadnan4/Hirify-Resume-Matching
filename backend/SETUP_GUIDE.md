# Hirify Backend Setup Guide

This guide will help you set up the Hirify backend without running into common issues that could crash the Python interpreter.

## Prerequisites

- Python 3.8 or higher
- Git
- Internet connection (for downloading models)

## Step-by-Step Setup

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Setup Script

**IMPORTANT**: Run this script to set up all required models and dependencies:

```bash
python setup_dependencies.py
```

This script will:
- Download required NLTK data
- Install spaCy language model
- Create necessary directories
- Check all dependencies
- Verify configuration

### 3. Manual Model Installation (if needed)

If the setup script fails, install models manually:

#### spaCy Model
```bash
python -m spacy download en_core_web_sm
```

#### NLTK Data (in Python)
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
```

### 4. Environment Configuration

Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/hirify

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# File Upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE=52428800

# Logging
LOG_LEVEL=INFO

# Performance
ENABLE_MEMORY_TRACKING=false
SLOW_REQUEST_THRESHOLD=2.0
```

### 5. Database Setup

```bash
# Run database migrations
alembic upgrade head
```

### 6. Start the Application

```bash
# Development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the main file
python main.py
```

## Common Issues and Fixes

### Issue 1: spaCy Model Not Found

**Error**: `OSError: [E050] Can't find model 'en_core_web_sm'`

**Fix**:
```bash
python -m spacy download en_core_web_sm
```

### Issue 2: NLTK Data Missing

**Error**: `LookupError: Resource punkt not found`

**Fix**:
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
```

### Issue 3: PyTorch Model Loading Fails

**Error**: Various BERT/Transformer errors

**Fix**: The application will automatically fall back to TF-IDF similarity if BERT models fail to load. No action needed - this is by design.

### Issue 4: Memory Issues with Large Files

**Prevention**: The application now has built-in memory management and file size limits.

### Issue 5: Async Event Loop Issues

**Fixed**: Removed problematic async context creation in Celery tasks.

## Features That Gracefully Degrade

The application is designed to work even if some components fail:

1. **spaCy Model Missing**: Falls back to regex-based parsing
2. **NLTK Data Missing**: Uses basic text processing
3. **BERT Models Missing**: Uses TF-IDF for similarity
4. **Sentence Transformers Missing**: Falls back to simpler methods

## Verifying Setup

Run the health check:

```bash
curl http://localhost:8000/health
```

Check the setup status:

```bash
python setup_dependencies.py
```

## Troubleshooting

### General Debugging

1. Check logs in the `logs/` directory
2. Verify all dependencies are installed: `pip list`
3. Check Python version: `python --version`
4. Verify models are installed: `python -m spacy info en_core_web_sm`

### Performance Issues

1. Monitor memory usage in logs
2. Check for file size limits in uploads
3. Verify database connection is stable

### Model Loading Issues

The application will log detailed information about model loading:
- Success messages when models load correctly
- Warning messages with instructions when models are missing
- Fallback notifications when using alternative methods

## Development vs Production

### Development
- Uses SQLite by default (if configured)
- Enables detailed logging
- Has relaxed security settings

### Production
- Use PostgreSQL
- Enable security headers
- Set proper SECRET_KEY
- Use environment variables for secrets
- Enable monitoring and logging

## Testing the Setup

After setup, test these endpoints:

1. Health check: `GET /health`
2. Upload a test resume: `POST /api/v1/resumes/upload`
3. Check processing status
4. Verify no crashes in logs

## Support

If you encounter issues not covered here:

1. Check the logs in `logs/app.log` and `logs/errors.log`
2. Run the setup script again: `python setup_dependencies.py`
3. Verify all requirements are met: `pip check`

The application is designed to be robust and provide helpful error messages when issues occur.
