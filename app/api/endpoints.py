from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
import uuid
import json
from datetime import datetime
from app.domain.models import AnalysisState
from app.orchestration.graph import graph
from app.persistence.database import get_db, AnalysisRun, AgentEvent, RiskSignal, Report

router = APIRouter()

class AnalysisRequest(BaseModel):
    ticker: str
    period: str = "1Y"

def _execute_analysis(ticker: str, period: str, run_id: str, db):
    # Initialize State
    initial_state = AnalysisState(
        run_id=run_id,
        ticker=ticker,
        analysis_period=period
    )
    
    try:
        # Run Graph
        result_state = graph.invoke(initial_state)
        
        # Persist results
        run = db.query(AnalysisRun).filter(AnalysisRun.run_id == run_id).first()
        if run:
            run.status = "completed" if not result_state.get("errors") else "error"
            run.completed_at = datetime.utcnow()
            
            if result_state.get("risk_analysis"):
                risk = result_state["risk_analysis"]
                run.risk_score = risk.score
                run.risk_level = risk.level
                
                # Persist signals
                for s in risk.signals:
                    sig = RiskSignal(
                        run_id=run_id,
                        signal_id=s.signal_id,
                        category=s.category,
                        severity=s.severity,
                        title=s.title,
                        description=s.description,
                        observed_value=s.observed_value,
                        threshold=s.threshold
                    )
                    db.add(sig)
            
            if result_state.get("report"):
                rep = Report(
                    run_id=run_id,
                    content=result_state["report"].model_dump_json()
                )
                db.add(rep)
                
            # Persist events
            for e in result_state.get("agent_events", []):
                ev = AgentEvent(
                    run_id=run_id,
                    agent_name=e.agent_name,
                    event_type=e.event_type,
                    status=e.status,
                    timestamp=e.timestamp,
                    duration_ms=e.duration_ms
                )
                db.add(ev)
                
            db.commit()
            
    except Exception as e:
        run = db.query(AnalysisRun).filter(AnalysisRun.run_id == run_id).first()
        if run:
            run.status = "error"
            db.commit()
        print(f"Workflow failed for {run_id}: {str(e)}")

@router.post("/analyses")
def start_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks, db = Depends(get_db)):
    run_id = str(uuid.uuid4())
    
    # Create DB entry
    run = AnalysisRun(
        run_id=run_id,
        ticker=request.ticker,
        analysis_period=request.period
    )
    db.add(run)
    db.commit()
    
    # Enqueue background task
    background_tasks.add_task(_execute_analysis, request.ticker, request.period, run_id, db)
    
    return {"run_id": run_id, "status": "pending"}

@router.get("/analyses/{run_id}")
def get_analysis(run_id: str, db = Depends(get_db)):
    run = db.query(AnalysisRun).filter(AnalysisRun.run_id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
        
    return {
        "run_id": run.run_id,
        "ticker": run.ticker,
        "status": run.status,
        "risk_score": run.risk_score,
        "risk_level": run.risk_level
    }

@router.get("/analyses/{run_id}/report")
def get_analysis_report(run_id: str, db = Depends(get_db)):
    report = db.query(Report).filter(Report.run_id == run_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return json.loads(report.content)

@router.get("/analyses/{run_id}/events")
def get_analysis_events(run_id: str, db = Depends(get_db)):
    events = db.query(AgentEvent).filter(AgentEvent.run_id == run_id).order_by(AgentEvent.id).all()
    return [{"agent_name": e.agent_name, "status": e.status, "duration_ms": e.duration_ms} for e in events]
