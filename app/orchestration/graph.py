import uuid
import time
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from app.domain.models import AnalysisState, AgentEvent
from app.agents.data_ingestion import ingest_data_agent
from app.agents.financial_analysis import analyze_financials_agent
from app.agents.news_context import gather_news_context_agent
from app.agents.risk_anomaly import calculate_risk_agent
from app.agents.report_generator import generate_report_agent

# Helper to wrap agents to record events
def wrap_agent(agent_func, agent_name: str):
    def wrapper(state: AnalysisState) -> Dict[str, Any]:
        start_time = time.time()
        
        # Execute actual agent
        updates = agent_func(state)
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        status = "error" if "errors" in updates and len(updates["errors"]) > len(state.errors) else "success"
        
        event = AgentEvent(
            run_id=state.run_id,
            agent_name=agent_name,
            event_type="execution",
            status=status,
            duration_ms=duration_ms
        )
        
        # Append event to state updates
        if "agent_events" not in updates:
            updates["agent_events"] = state.agent_events + [event]
        else:
            updates["agent_events"].append(event)
            
        return updates
    return wrapper

def create_analysis_graph() -> StateGraph:
    workflow = StateGraph(AnalysisState)
    
    # Add nodes
    workflow.add_node("data_ingestion", wrap_agent(ingest_data_agent, "Data Ingestion Agent"))
    workflow.add_node("financial_analysis", wrap_agent(analyze_financials_agent, "Financial Analysis Agent"))
    workflow.add_node("news_context", wrap_agent(gather_news_context_agent, "News & Context Agent"))
    workflow.add_node("risk_anomaly", wrap_agent(calculate_risk_agent, "Risk & Anomaly Agent"))
    workflow.add_node("report_generator", wrap_agent(generate_report_agent, "Report Generator Agent"))
    
    # Define edges (linear flow for MVP)
    workflow.set_entry_point("data_ingestion")
    
    # Linear flow
    workflow.add_edge("data_ingestion", "financial_analysis")
    workflow.add_edge("financial_analysis", "news_context")
    workflow.add_edge("news_context", "risk_anomaly")
    workflow.add_edge("risk_anomaly", "report_generator")
    workflow.add_edge("report_generator", END)
    
    # Compile
    return workflow.compile()

graph = create_analysis_graph()
