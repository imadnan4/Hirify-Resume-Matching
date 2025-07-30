# Import tasks with error handling for missing dependencies
try:
    from .resume_processing import process_resume_task, cleanup_failed_uploads
    RESUME_PROCESSING_AVAILABLE = True
except ImportError:
    RESUME_PROCESSING_AVAILABLE = False

try:
    from .resume_tasks import process_resume, bulk_process_resumes
    RESUME_TASKS_AVAILABLE = True
except ImportError:
    RESUME_TASKS_AVAILABLE = False

# Build __all__ list based on available imports
__all__ = []

if RESUME_PROCESSING_AVAILABLE:
    __all__.extend(["process_resume_task", "cleanup_failed_uploads"])

if RESUME_TASKS_AVAILABLE:
    __all__.extend(["process_resume", "bulk_process_resumes"])
