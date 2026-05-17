"""
app/services/pipeline_worker.py

Master pipeline orchestrator.

Runs all selected pipelines concurrently (asyncio.gather) for a given company,
collects results, assigns opportunity categories, runs AI inference, and
persists everything to the database.

Each pipeline source is isolated in app/pipelines/ — no stubs, all real data.
"""

import logging
import asyncio
from typing import Any
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.pipeline_run import PipelineRun

logger = logging.getLogger(__name__)

# ── Standalone pipeline imports ──────────────────────────────────────────────
from app.pipelines.career_pipeline import run_career_pipeline_enriched
from app.pipelines.blog_pipeline import run_blog_pipeline_enriched
from app.pipelines.reddit_pipeline import run_reddit_pipeline
from app.pipelines.github_issues_pipeline import run_github_issues_pipeline
from app.pipelines.funding_pipeline import run_funding_pipeline
from app.pipelines.hiring_signals_pipeline import run_hiring_signals_pipeline

# ── AI inference + DB helpers ────────────────────────────────────────────────
from app.schemas.signal import AIOpportunityOutput
from app.services.ai.inference import run_ai_inference
from app.services.company_service import (
    get_or_create_company,
    update_company_ats,
    update_company_blog,
    save_signals,
    save_market_pain_signals,
)


async def execute_pipeline_run(
    pipeline_run_id: str,
    company_name: str,
    selected_pipelines: list[str],
) -> None:
    """
    Execute a complete pipeline run for a company.

    Runs all selected source pipelines concurrently, collects results,
    runs AI inference, persists signals to the database, and updates
    the PipelineRun record with full results.

    Args:
        pipeline_run_id: UUID string of the PipelineRun record to update.
        company_name: Target company name for this run.
        selected_pipelines: List of pipeline keys to run.
            Valid values: "career", "blog", "market_pain", "git_issues", "funding", "hiring"
    """
    db: Session = SessionLocal()
    try:
        # ── Load the run record ──────────────────────────────────────────────
        run_record = db.query(PipelineRun).filter(PipelineRun.id == pipeline_run_id).first()
        if not run_record:
            logger.error(f"[PipelineWorker] PipelineRun {pipeline_run_id} not found.")
            return

        run_record.status = "running"
        db.commit()

        logger.info(
            f"[PipelineWorker] Starting run {pipeline_run_id} for '{company_name}' | "
            f"pipelines={selected_pipelines}"
        )
        company = get_or_create_company(db, company_name)

        # ── Build concurrent task list ────────────────────────────────────────
        tasks: list[Any] = []
        task_names: list[str] = []

        if "career" in selected_pipelines:
            tasks.append(run_career_pipeline_enriched(company_name))
            task_names.append("career")

        if "blog" in selected_pipelines:
            tasks.append(run_blog_pipeline_enriched(company_name))
            task_names.append("blog")

        if "market_pain" in selected_pipelines:
            tasks.append(run_reddit_pipeline(company_name))
            task_names.append("market_pain")

        if "git_issues" in selected_pipelines:
            tasks.append(run_github_issues_pipeline(company_name, db))
            task_names.append("git_issues")

        if "funding" in selected_pipelines:
            tasks.append(run_funding_pipeline(company_name, db))
            task_names.append("funding")

        if "hiring" in selected_pipelines:
            tasks.append(run_hiring_signals_pipeline(company_name, db))
            task_names.append("hiring")

        # ── Run all pipelines concurrently ────────────────────────────────────
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # ── Unpack results ────────────────────────────────────────────────────
        career_signals, ats_platform, ats_url = [], None, None
        blog_signals, blog_url = [], None
        market_pain_signals: list[Any] = []
        git_signals: list[dict] = []
        funding_signals: list[dict] = []
        hiring_signals: list[dict] = []
        errors: dict[str, str] = {}

        for i, task_name in enumerate(task_names):
            res = results[i]
            if isinstance(res, Exception):
                logger.error(f"[PipelineWorker] Pipeline '{task_name}' raised: {res}")
                errors[task_name] = str(res)
                continue

            logger.info(f"[PipelineWorker] Pipeline '{task_name}' succeeded")

            if task_name == "career":
                career_signals, ats_platform, ats_url = res
            elif task_name == "blog":
                blog_signals, blog_url = res
            elif task_name == "market_pain":
                market_pain_signals = res
            elif task_name == "git_issues":
                git_signals = res or []
            elif task_name == "funding":
                funding_signals = res or []
            elif task_name == "hiring":
                hiring_signals = res or []

        # ── Update company metadata ───────────────────────────────────────────
        if ats_platform and ats_url:
            update_company_ats(db, company, ats_platform, ats_url)
        if blog_url:
            update_company_blog(db, company, blog_url)

        # ── Combine + rank career/blog signals for AI inference ───────────────
        all_signals = career_signals + blog_signals
        all_signals.sort(key=lambda x: x.confidence, reverse=True)
        all_signals = all_signals[:10]

        ai_output: AIOpportunityOutput | None = await run_ai_inference(
            all_signals,
            company_name,
            market_pain_signals=market_pain_signals,
        )
        ai_dict = ai_output.model_dump() if ai_output else None

        # ── Persist career/blog signals ───────────────────────────────────────
        saved_records = save_signals(db, company, all_signals, ai_analysis=ai_dict)

        # ── Persist market pain signals ───────────────────────────────────────
        if market_pain_signals:
            try:
                save_market_pain_signals(db, company, market_pain_signals)
            except Exception as exc:
                logger.error(f"[PipelineWorker] Market pain persistence failed: {exc}")
                errors["market_pain_db"] = str(exc)

        # ── Serialize for run results ─────────────────────────────────────────
        from app.schemas.signal import SignalResponse
        serialized_signals = [
            SignalResponse.model_validate(s).model_dump(mode="json")
            for s in saved_records
        ]

        serialized_pain: list[dict] = []
        for r in market_pain_signals:
            serialized_pain.append(
                r.model_dump(mode="json") if hasattr(r, "model_dump") else r
            )

        # ── Update run record ─────────────────────────────────────────────────
        run_record.status = "completed"
        run_record.results = {
            "company_name": company_name,
            "ai_analysis": ai_dict,
            "career_signals_count": len(career_signals),
            "blog_signals_count": len(blog_signals),
            "market_pain_count": len(market_pain_signals),
            "git_issues_count": len(git_signals),
            "funding_count": len(funding_signals),
            "hiring_count": len(hiring_signals),
            "ats_platform": ats_platform,
            "ats_url": ats_url,
            "blog_url": blog_url,
            "signals": serialized_signals,
            "market_pain_signals": serialized_pain,
            "git_signals": git_signals,
            "funding_signals": funding_signals,
            "hiring_signals": hiring_signals,
            "total_signals": len(all_signals),
        }
        run_record.errors = errors
        db.commit()

        try:
            from app.services.service_intelligence.service import refresh_relanto_opportunity_scores

            refreshed = refresh_relanto_opportunity_scores(db, company_name=company_name)
            logger.info(f"[PipelineWorker] Refreshed {refreshed} Relanto opportunity score rows")
        except Exception as exc:
            logger.error(f"[PipelineWorker] Relanto score refresh failed: {exc}")

        logger.info(
            f"[PipelineWorker] Run {pipeline_run_id} COMPLETED | "
            f"career={len(career_signals)}, blog={len(blog_signals)}, "
            f"reddit={len(market_pain_signals)}, github={len(git_signals)}, "
            f"funding={len(funding_signals)}, hiring={len(hiring_signals)}"
        )

    except Exception as exc:
        logger.error(f"[PipelineWorker] Critical error in run {pipeline_run_id}: {exc}", exc_info=True)
        if "run_record" in locals() and run_record:
            run_record.status = "failed"
            run_record.errors = {"system": str(exc)}
            db.commit()
    finally:
        db.close()
