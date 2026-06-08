"""
app/services/pipeline_worker.py

Master pipeline orchestrator using LangGraph.

Runs all selected pipelines in parallel via a state graph, collects results,
runs AI inference, and persists everything to the database.
"""

import logging
from typing import Any, Annotated
from sqlalchemy.orm import Session

from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

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
from app.services.service_intelligence.service import refresh_relanto_opportunity_scores
from app.schemas.signal import SignalResponse


def merge_errors(old: dict, new: dict) -> dict:
    """Merge new errors into existing error dict for Annotated state updates."""
    res = old.copy() if old else {}
    if new:
        res.update(new)
    return res


class GraphState(TypedDict):
    """
    State object flowing through the LangGraph execution.
    """
    pipeline_run_id: str
    company_name: str
    selected_pipelines: list[str]
    
    career_signals: list[Any]
    ats_platform: str | None
    ats_url: str | None
    
    blog_signals: list[Any]
    blog_url: str | None
    
    market_pain_signals: list[Any]
    git_signals: list[dict]
    funding_signals: list[dict]
    hiring_signals: list[dict]
    
    errors: Annotated[dict[str, str], merge_errors]
    
    ai_output: dict | None


# ── Node Definitions ─────────────────────────────────────────────────────────

async def setup_node(state: GraphState) -> dict:
    pipeline_run_id = state["pipeline_run_id"]
    company_name = state["company_name"]
    db: Session = SessionLocal()
    try:
        run_record = db.query(PipelineRun).filter(PipelineRun.id == pipeline_run_id).first()
        if not run_record:
            logger.error(f"[PipelineWorker] PipelineRun {pipeline_run_id} not found.")
            return {"errors": {"system": "PipelineRun not found"}}
            
        run_record.status = "running"
        db.commit()
        
        logger.info(
            f"[PipelineWorker] Starting run {pipeline_run_id} for '{company_name}' | "
            f"pipelines={state['selected_pipelines']}"
        )
        get_or_create_company(db, company_name)
    except Exception as exc:
        return {"errors": {"setup": str(exc)}}
    finally:
        db.close()
        
    return {}

async def career_node(state: GraphState) -> dict:
    try:
        signals, ats_platform, ats_url = await run_career_pipeline_enriched(state["company_name"])
        logger.info("[PipelineWorker] Pipeline 'career' succeeded")
        return {
            "career_signals": signals,
            "ats_platform": ats_platform,
            "ats_url": ats_url
        }
    except Exception as exc:
        logger.error(f"[PipelineWorker] Pipeline 'career' raised: {exc}")
        return {"errors": {"career": str(exc)}}

async def blog_node(state: GraphState) -> dict:
    try:
        signals, blog_url = await run_blog_pipeline_enriched(state["company_name"])
        logger.info("[PipelineWorker] Pipeline 'blog' succeeded")
        return {
            "blog_signals": signals,
            "blog_url": blog_url
        }
    except Exception as exc:
        logger.error(f"[PipelineWorker] Pipeline 'blog' raised: {exc}")
        return {"errors": {"blog": str(exc)}}

async def market_pain_node(state: GraphState) -> dict:
    try:
        signals = await run_reddit_pipeline(state["company_name"])
        logger.info("[PipelineWorker] Pipeline 'market_pain' succeeded")
        return {"market_pain_signals": signals}
    except Exception as exc:
        logger.error(f"[PipelineWorker] Pipeline 'market_pain' raised: {exc}")
        return {"errors": {"market_pain": str(exc)}}

async def git_node(state: GraphState) -> dict:
    db = SessionLocal()
    try:
        signals = await run_github_issues_pipeline(state["company_name"], db)
        logger.info("[PipelineWorker] Pipeline 'git_issues' succeeded")
        return {"git_signals": signals or []}
    except Exception as exc:
        logger.error(f"[PipelineWorker] Pipeline 'git_issues' raised: {exc}")
        return {"errors": {"git_issues": str(exc)}}
    finally:
        db.close()

async def funding_node(state: GraphState) -> dict:
    db = SessionLocal()
    try:
        signals = await run_funding_pipeline(state["company_name"], db)
        logger.info("[PipelineWorker] Pipeline 'funding' succeeded")
        return {"funding_signals": signals or []}
    except Exception as exc:
        logger.error(f"[PipelineWorker] Pipeline 'funding' raised: {exc}")
        return {"errors": {"funding": str(exc)}}
    finally:
        db.close()

async def hiring_node(state: GraphState) -> dict:
    db = SessionLocal()
    try:
        signals = await run_hiring_signals_pipeline(state["company_name"], db)
        logger.info("[PipelineWorker] Pipeline 'hiring' succeeded")
        return {"hiring_signals": signals or []}
    except Exception as exc:
        logger.error(f"[PipelineWorker] Pipeline 'hiring' raised: {exc}")
        return {"errors": {"hiring": str(exc)}}
    finally:
        db.close()

async def inference_node(state: GraphState) -> dict:
    career_signals = state.get("career_signals", [])
    blog_signals = state.get("blog_signals", [])
    market_pain_signals = state.get("market_pain_signals", [])
    
    all_signals = career_signals + blog_signals
    all_signals.sort(key=lambda x: getattr(x, 'confidence', 0), reverse=True)
    all_signals = all_signals[:10]
    
    try:
        ai_output: AIOpportunityOutput | None = await run_ai_inference(
            all_signals,
            state["company_name"],
            market_pain_signals=market_pain_signals,
        )
        ai_dict = ai_output.model_dump() if ai_output else None
        return {"ai_output": ai_dict}
    except Exception as exc:
        logger.error(f"[PipelineWorker] Inference failed: {exc}")
        return {"errors": {"inference": str(exc)}}

async def persist_node(state: GraphState) -> dict:
    db: Session = SessionLocal()
    errors = state.get("errors", {})
    try:
        company = get_or_create_company(db, state["company_name"])
        
        ats_platform = state.get("ats_platform")
        ats_url = state.get("ats_url")
        if ats_platform and ats_url:
            update_company_ats(db, company, ats_platform, ats_url)
            
        blog_url = state.get("blog_url")
        if blog_url:
            update_company_blog(db, company, blog_url)
            
        career_signals = state.get("career_signals", [])
        blog_signals = state.get("blog_signals", [])
        all_signals = career_signals + blog_signals
        all_signals.sort(key=lambda x: getattr(x, 'confidence', 0), reverse=True)
        all_signals = all_signals[:10]
        
        saved_records = save_signals(db, company, all_signals, ai_analysis=state.get("ai_output"))
        
        market_pain_signals = state.get("market_pain_signals", [])
        if market_pain_signals:
            try:
                save_market_pain_signals(db, company, market_pain_signals)
            except Exception as exc:
                logger.error(f"[PipelineWorker] Market pain persistence failed: {exc}")
                errors["market_pain_db"] = str(exc)
        
        serialized_signals = [
            SignalResponse.model_validate(s).model_dump(mode="json")
            for s in saved_records
        ]
        
        serialized_pain = []
        for r in market_pain_signals:
            serialized_pain.append(
                r.model_dump(mode="json") if hasattr(r, "model_dump") else r
            )
            
        run_record = db.query(PipelineRun).filter(PipelineRun.id == state["pipeline_run_id"]).first()
        if run_record:
            run_record.status = "completed" if not errors.get("system") else "failed"
            run_record.results = {
                "company_name": state["company_name"],
                "ai_analysis": state.get("ai_output"),
                "career_signals_count": len(career_signals),
                "blog_signals_count": len(blog_signals),
                "market_pain_count": len(market_pain_signals),
                "git_issues_count": len(state.get("git_signals", [])),
                "funding_count": len(state.get("funding_signals", [])),
                "hiring_count": len(state.get("hiring_signals", [])),
                "ats_platform": ats_platform,
                "ats_url": ats_url,
                "blog_url": blog_url,
                "signals": serialized_signals,
                "market_pain_signals": serialized_pain,
                "git_signals": state.get("git_signals", []),
                "funding_signals": state.get("funding_signals", []),
                "hiring_signals": state.get("hiring_signals", []),
                "total_signals": len(all_signals),
            }
            run_record.errors = errors
            db.commit()
            
        try:
            from app.services.service_intelligence.service import refresh_relanto_opportunity_scores
            refreshed = refresh_relanto_opportunity_scores(db, company_name=state["company_name"])
            logger.info(f"[PipelineWorker] Refreshed {refreshed} Relanto opportunity score rows")
        except Exception as exc:
            logger.error(f"[PipelineWorker] Relanto score refresh failed: {exc}")
            
        logger.info(
            f"[PipelineWorker] Run {state['pipeline_run_id']} COMPLETED | "
            f"career={len(career_signals)}, blog={len(blog_signals)}, "
            f"reddit={len(market_pain_signals)}, github={len(state.get('git_signals', []))}, "
            f"funding={len(state.get('funding_signals', []))}, hiring={len(state.get('hiring_signals', []))}"
        )
    except Exception as exc:
        logger.error(f"[PipelineWorker] Critical error in persist node: {exc}", exc_info=True)
        return {"errors": {"persist": str(exc)}}
    finally:
        db.close()
        
    return {"errors": errors} if errors else {}


# ── Edge Routing ─────────────────────────────────────────────────────────────

def route_pipelines(state: GraphState) -> list[str]:
    selected = state.get("selected_pipelines", [])
    nodes = []
    if "career" in selected: nodes.append("career_node")
    if "blog" in selected: nodes.append("blog_node")
    if "market_pain" in selected: nodes.append("market_pain_node")
    if "git_issues" in selected: nodes.append("git_node")
    if "funding" in selected: nodes.append("funding_node")
    if "hiring" in selected: nodes.append("hiring_node")
    
    if not nodes:
        return ["inference_node"]
    return nodes


# ── Graph Compilation ────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    builder = StateGraph(GraphState)
    
    builder.add_node("setup_node", setup_node)
    builder.add_node("career_node", career_node)
    builder.add_node("blog_node", blog_node)
    builder.add_node("market_pain_node", market_pain_node)
    builder.add_node("git_node", git_node)
    builder.add_node("funding_node", funding_node)
    builder.add_node("hiring_node", hiring_node)
    builder.add_node("inference_node", inference_node)
    builder.add_node("persist_node", persist_node)
    
    builder.set_entry_point("setup_node")
    
    builder.add_conditional_edges("setup_node", route_pipelines)
    
    builder.add_edge("career_node", "inference_node")
    builder.add_edge("blog_node", "inference_node")
    builder.add_edge("market_pain_node", "inference_node")
    builder.add_edge("git_node", "inference_node")
    builder.add_edge("funding_node", "inference_node")
    builder.add_edge("hiring_node", "inference_node")
    
    builder.add_edge("inference_node", "persist_node")
    builder.add_edge("persist_node", END)
    
    return builder.compile()


graph = build_graph()


# ── Main Entry ───────────────────────────────────────────────────────────────

async def execute_pipeline_run(
    pipeline_run_id: str,
    company_name: str,
    selected_pipelines: list[str],
) -> None:
    """
    Execute a complete pipeline run for a company using LangGraph.
    """
    initial_state = {
        "pipeline_run_id": pipeline_run_id,
        "company_name": company_name,
        "selected_pipelines": selected_pipelines,
        "career_signals": [],
        "ats_platform": None,
        "ats_url": None,
        "blog_signals": [],
        "blog_url": None,
        "market_pain_signals": [],
        "git_signals": [],
        "funding_signals": [],
        "hiring_signals": [],
        "errors": {},
        "ai_output": None
    }
    
    try:
        await graph.ainvoke(initial_state)
    except Exception as exc:
        logger.error(f"[PipelineWorker] Graph execution failed for run {pipeline_run_id}: {exc}", exc_info=True)
        # Attempt to mark as failed in DB
        db = SessionLocal()
        try:
            run_record = db.query(PipelineRun).filter(PipelineRun.id == pipeline_run_id).first()
            if run_record:
                run_record.status = "failed"
                run_record.errors = {"system": str(exc)}
                db.commit()
        except Exception:
            pass
        finally:
            db.close()
