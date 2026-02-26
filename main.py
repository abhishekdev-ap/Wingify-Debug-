from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import os
import uuid

from crewai import Crew, Process
from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from task import verification, analyze_financial_document, investment_analysis, risk_assessment
from database import init_db, save_analysis, update_analysis, get_analysis, get_all_analyses

app = FastAPI(
    title="Financial Document Analyzer",
    description="AI-powered financial document analysis system using CrewAI agents",
    version="1.0.0",
)

# Initialize database on startup
init_db()


def run_crew(query: str, file_path: str = "data/TSLA-Q2-2025-Update.pdf"):
    """Run the full financial analysis crew with all agents and tasks."""
    financial_crew = Crew(
        agents=[verifier, financial_analyst, investment_advisor, risk_assessor],
        tasks=[verification, analyze_financial_document, investment_analysis, risk_assessment],
        process=Process.sequential,
        verbose=True,
    )

    result = financial_crew.kickoff({"query": query, "file_path": file_path})
    return result


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Financial Document Analyzer API is running"}


@app.post("/analyze")
async def analyze_document_endpoint(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights")
):
    """Analyze financial document synchronously and return results."""

    file_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{file_id}.pdf"

    try:
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)

        # Save uploaded file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Validate query
        if not query or query.strip() == "":
            query = "Analyze this financial document for investment insights"

        # Process the financial document with all analysts
        response = run_crew(query=query.strip(), file_path=file_path)

        # Save result to database
        save_analysis(
            task_id=file_id,
            filename=file.filename,
            query=query,
            result=str(response),
            status="completed"
        )

        return {
            "status": "success",
            "task_id": file_id,
            "query": query,
            "analysis": str(response),
            "file_processed": file.filename
        }

    except Exception as e:
        # Save failed analysis to database
        save_analysis(
            task_id=file_id,
            filename=file.filename,
            query=query,
            status="failed",
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Error processing financial document: {str(e)}")

    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass


@app.post("/analyze/async")
async def analyze_document_async_endpoint(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights")
):
    """Queue a financial document for async analysis using Celery."""

    file_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{file_id}.pdf"

    try:
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)

        # Save uploaded file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Validate query
        if not query or query.strip() == "":
            query = "Analyze this financial document for investment insights"

        # Save initial record to database
        save_analysis(
            task_id=file_id,
            filename=file.filename,
            query=query,
            status="pending"
        )

        # Queue the analysis task
        from celery_worker import analyze_document_async
        analyze_document_async.delay(
            task_id=file_id,
            query=query.strip(),
            file_path=file_path,
            filename=file.filename
        )

        return {
            "status": "queued",
            "task_id": file_id,
            "message": "Document analysis has been queued. Use /status/{task_id} to check progress.",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error queuing document analysis: {str(e)}")


@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """Check the status of an async analysis task."""
    analysis = get_analysis(task_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Task not found")

    response = {
        "task_id": analysis.task_id,
        "status": analysis.status,
        "filename": analysis.filename,
        "query": analysis.query,
        "created_at": str(analysis.created_at),
    }

    if analysis.status == "completed":
        response["result"] = analysis.result
        response["completed_at"] = str(analysis.completed_at)
    elif analysis.status == "failed":
        response["error"] = analysis.error
        response["completed_at"] = str(analysis.completed_at)

    return response


@app.get("/results")
async def list_results(limit: int = 50, offset: int = 0):
    """List all analysis results with pagination."""
    analyses = get_all_analyses(limit=limit, offset=offset)
    return {
        "count": len(analyses),
        "results": [
            {
                "task_id": a.task_id,
                "filename": a.filename,
                "query": a.query,
                "status": a.status,
                "created_at": str(a.created_at),
                "completed_at": str(a.completed_at) if a.completed_at else None,
            }
            for a in analyses
        ]
    }


@app.get("/results/{task_id}")
async def get_result(task_id: str):
    """Get a specific analysis result by task ID."""
    analysis = get_analysis(task_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis result not found")

    return {
        "task_id": analysis.task_id,
        "filename": analysis.filename,
        "query": analysis.query,
        "status": analysis.status,
        "result": analysis.result,
        "error": analysis.error,
        "created_at": str(analysis.created_at),
        "completed_at": str(analysis.completed_at) if analysis.completed_at else None,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)