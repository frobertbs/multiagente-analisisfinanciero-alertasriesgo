from typing import Dict, Any
from app.domain.models import AnalysisState, FinancialAnalysis
from app.analytics.financial_metrics import calculate_financial_metrics, calculate_market_metrics

def analyze_financials_agent(state: AnalysisState) -> Dict[str, Any]:
    print(f"--- Analyzing financials for {state.ticker} ---")
    
    if not state.financial_data or not state.market_data:
        return {
            "errors": state.errors + [{"agent": "Financial Analysis Agent", "message": "Missing financial or market data"}]
        }
        
    try:
        financial_metrics = calculate_financial_metrics(state.financial_data.periods)
        market_metrics = calculate_market_metrics(state.market_data.prices)
        
        all_metrics = financial_metrics + market_metrics
        analysis = FinancialAnalysis(metrics=all_metrics)
        
        return {
            "financial_analysis": analysis
        }
    except Exception as e:
        return {
            "errors": state.errors + [{"agent": "Financial Analysis Agent", "message": str(e)}]
        }
