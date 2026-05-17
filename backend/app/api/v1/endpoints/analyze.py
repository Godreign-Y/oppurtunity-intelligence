"""
app/api/v1/endpoints/analyze.py

API endpoint for triggering the full company intelligence analysis pipeline.
Runs career, blog, and market pain pipelines, then applies AI inference.
"""

import logging
import asyncio
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.signal import AnalyzeCompanyRequest, AIOpportunityOutput
from app.services.career.pipeline import run_career_pipeline
from app.services.blog.pipeline import run_blog_pipeline
from app.services.market_pain.pipeline import run_market_pain_pipeline
from app.services.ai.inference import run_ai_inference
from app.services.company_service import (
    get_or_create_company,
    update_company_ats,
    update_company_blog,
    save_signals,
    save_market_pain_signals,
)

from fastapi import BackgroundTasks
from app.models.pipeline_run import PipelineRun
from app.schemas.signal import PipelineRunResponse
from app.services.pipeline_worker import execute_pipeline_run
from app.utils.security import mask_sensitive_text

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/analyze/start", response_model=PipelineRunResponse, summary="Trigger async full company intelligence analysis")
async def start_analyze_company(
    request: AnalyzeCompanyRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    company_name = request.company_name.strip()
    if not company_name:
        raise HTTPException(status_code=400, detail="company_name must not be empty.")

    run_record = PipelineRun(
        company_name=company_name,
        pipelines_selected=request.pipelines_selected,
        status="pending"
    )
    db.add(run_record)
    db.commit()
    db.refresh(run_record)

    def run_sync():
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(execute_pipeline_run(str(run_record.id), company_name, request.pipelines_selected))
        finally:
            loop.close()

    background_tasks.add_task(run_sync)

    return PipelineRunResponse.model_validate(run_record)

@router.get("/analyze/{run_id}", response_model=PipelineRunResponse, summary="Get Pipeline Run status")
def get_pipeline_run(run_id: str, db: Session = Depends(get_db)):
    run_record = db.query(PipelineRun).filter(PipelineRun.id == run_id).first()
    if not run_record:
        raise HTTPException(status_code=404, detail="Pipeline run not found")
    return PipelineRunResponse.model_validate(run_record)

@router.get("/analyze/runs/{company_name}", response_model=list[PipelineRunResponse])
def list_pipeline_runs(company_name: str, db: Session = Depends(get_db)):
    runs = db.query(PipelineRun).filter(PipelineRun.company_name == company_name).order_by(PipelineRun.created_at.desc()).all()
    return [PipelineRunResponse.model_validate(r) for r in runs]


@router.get("/analyze/logs/tail")
def get_pipeline_logs(
    run_id: str | None = Query(default=None),
    company_name: str | None = Query(default=None),
    limit: int = Query(default=120, ge=1, le=500),
) -> dict:
    log_path = Path(__file__).resolve().parents[4] / "pipeline.log"
    if not log_path.exists():
        return {"lines": []}

    lines = log_path.read_text(encoding="utf-8", errors="ignore").splitlines()[-limit * 3 :]
    if run_id:
        lines = [line for line in lines if run_id in line]
    if company_name:
        needle = company_name.lower()
        lines = [line for line in lines if needle in line.lower()]

    return {"lines": [mask_sensitive_text(line) for line in lines[-limit:]]}
