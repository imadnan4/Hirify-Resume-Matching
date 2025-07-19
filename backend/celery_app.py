from celery import Celery
from app.core.config import settings
import os

# Create Celery instance
celery_app = Celery(
    "hirify",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks"]
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,
    task_routes={
        "app.tasks.process_resume": {"queue": "resume_processing"},
        "app.tasks.scrape_jobs": {"queue": "job_scraping"},
        "app.tasks.calculate_matches": {"queue": "matching"},
        "app.tasks.bulk_process": {"queue": "bulk_processing"},
    },
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=False,
    task_default_retry_delay=60,
    task_max_retries=3,
)

# Task discovery
celery_app.autodiscover_tasks()

if __name__ == "__main__":
    celery_app.start()
