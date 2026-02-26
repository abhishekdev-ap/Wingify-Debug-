"""Database module for storing financial analysis results."""
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./financial_analyzer.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class AnalysisResult(Base):
    """Model to store financial document analysis results."""
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_id = Column(String(36), unique=True, index=True, nullable=False)
    filename = Column(String(255), nullable=False)
    query = Column(Text, nullable=False)
    result = Column(Text, nullable=True)
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


def init_db():
    """Create database tables if they don't exist."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_analysis(task_id: str, filename: str, query: str, result: str = None,
                  status: str = "completed", error: str = None):
    """Save an analysis result to the database."""
    db = SessionLocal()
    try:
        analysis = AnalysisResult(
            task_id=task_id,
            filename=filename,
            query=query,
            result=result,
            status=status,
            error=error,
            completed_at=datetime.utcnow() if status in ("completed", "failed") else None,
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        return analysis
    finally:
        db.close()


def update_analysis(task_id: str, result: str = None, status: str = "completed", error: str = None):
    """Update an existing analysis result."""
    db = SessionLocal()
    try:
        analysis = db.query(AnalysisResult).filter(AnalysisResult.task_id == task_id).first()
        if analysis:
            if result is not None:
                analysis.result = result
            analysis.status = status
            if error is not None:
                analysis.error = error
            if status in ("completed", "failed"):
                analysis.completed_at = datetime.utcnow()
            db.commit()
            db.refresh(analysis)
        return analysis
    finally:
        db.close()


def get_analysis(task_id: str):
    """Get an analysis result by task_id."""
    db = SessionLocal()
    try:
        return db.query(AnalysisResult).filter(AnalysisResult.task_id == task_id).first()
    finally:
        db.close()


def get_all_analyses(limit: int = 50, offset: int = 0):
    """Get all analysis results with pagination."""
    db = SessionLocal()
    try:
        return db.query(AnalysisResult).order_by(
            AnalysisResult.created_at.desc()
        ).offset(offset).limit(limit).all()
    finally:
        db.close()
