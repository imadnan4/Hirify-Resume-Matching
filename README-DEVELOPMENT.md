# Hirify - Development Setup Guide

This guide will help you set up and run the Hirify application locally.

## 🚀 Quick Start

### Option 1: Using PowerShell Script (Recommended)
```powershell
.\run.ps1
```

### Option 2: Using Batch Script
```cmd
run.bat
```

### Option 3: Manual Setup

#### Backend Setup
1. Navigate to the backend directory:
```cmd
cd backend
```

2. Activate virtual environment:
```cmd
venv\Scripts\activate
```

3. Run database migrations:
```cmd
alembic upgrade head
```

4. Start the FastAPI server:
```cmd
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Setup
1. Open a new terminal and navigate to the frontend directory:
```cmd
cd frontend
```

2. Install dependencies (if not already installed):
```cmd
npm install
```

3. Start the development server:
```cmd
npm run dev
```

## 📋 Prerequisites

- **Python 3.8+**: For the backend API
- **Node.js 16+**: For the frontend application
- **npm**: Node package manager

## 🔧 Configuration

The application uses SQLite for development, so no additional database setup is required. The configuration is stored in `backend/.env`.

## 🌐 Access URLs

After running the scripts:
- **Frontend**: http://localhost:5173 (Vite dev server)
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative API Docs**: http://localhost:8000/redoc

## 🚨 Troubleshooting

### Backend Issues

1. **Virtual Environment Not Found**:
   - The scripts will automatically create one, or manually run:
   ```cmd
   cd backend
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Database Migration Errors**:
   ```cmd
   cd backend
   venv\Scripts\activate
   alembic upgrade head
   ```

3. **Port Already in Use**:
   - Kill any process using port 8000:
   ```cmd
   netstat -ano | findstr :8000
   taskkill /PID <PID_NUMBER> /F
   ```

### Frontend Issues

1. **Dependencies Not Installed**:
   ```cmd
   cd frontend
   npm install
   ```

2. **Port Already in Use**:
   - Vite will automatically try the next available port (5174, 5175, etc.)

## 🔍 Development Notes

- The backend runs with `--reload` flag, so changes to Python files will automatically restart the server
- The frontend runs with Vite's hot reload, so changes to React/TypeScript files will be instantly reflected
- Database is SQLite-based for development (file: `backend/hirify.db`)
- File uploads are stored in `backend/uploads/` directory

## 🛑 Stopping the Application

To stop the application:
1. Press `Ctrl+C` in the frontend terminal
2. Close the backend PowerShell/Command Prompt window
3. Or press `Ctrl+C` in the backend terminal

## 📚 API Documentation

Once the backend is running, you can access the interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
