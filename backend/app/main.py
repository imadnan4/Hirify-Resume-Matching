from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import routers
from app.api.v1.endpoints import resumes, jobs, matching, auth, candidates
from app.core.database import engine, Base
from app.core.config import settings
from app.core.logging_config import get_logger

# Setup logging
logger = get_logger()

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Hirify API...")
    yield
    # Shutdown
    print("Shutting down Hirify API...")

# Create FastAPI app
app = FastAPI(
    title="Hirify API",
    description="AI-powered resume parsing and job matching platform",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(resumes.router, prefix="/api/v1/resumes", tags=["Resumes"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])
app.include_router(matching.router, prefix="/api/v1/matching", tags=["Matching"])
app.include_router(candidates.router, prefix="/api/v1/candidates", tags=["Candidates"])

@app.get("/")
async def root():
    return {"message": "Hirify API is running!", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
