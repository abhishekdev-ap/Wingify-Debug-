"""Celery worker for async financial document analysis."""
import os
from dotenv import load_dotenv
load_dotenv()

from celery import Celery
from database import save_analysis, update_analysis

# Redis URL for Celery broker and backend
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "financial_analyzer",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,  # Process one task at a time per worker
)


@celery_app.task(bind=True, name="analyze_document_async")
def analyze_document_async(self, task_id: str, query: str, file_path: str, filename: str):
    """Async task to analyze a financial document using the CrewAI crew."""
    try:
        # Update status to processing
        update_analysis(task_id=task_id, status="processing")

        # Import here to avoid circular imports
        from main import run_crew

        # Run the CrewAI analysis
        result = run_crew(query=query, file_path=file_path)

        # Save result to database
        update_analysis(task_id=task_id, result=str(result), status="completed")

        # Clean up uploaded file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass

        return {
            "task_id": task_id,
            "status": "completed",
            "result": str(result),
            "file_processed": filename,
        }

    except Exception as e:
        # Update status to failed
        update_analysis(task_id=task_id, status="failed", error=str(e))

        # Clean up uploaded file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass

        return {
            "task_id": task_id,
            "status": "failed",
            "error": str(e),
        }
