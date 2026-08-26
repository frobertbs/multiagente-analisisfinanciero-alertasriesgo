from typing import Dict, Any
from app.domain.models import AnalysisState, RiskAnalysis
from app.analytics.rule_engine import evaluate_rules, calculate_risk_score
from app.analytics.anomaly_detection import detect_market_anomalies

def calculate_risk_agent(state: AnalysisState) -> Dict[str, Any]:
    print(f"--- Calculating Risk for {state.ticker} ---")
    
    if not state.financial_analysis or not state.market_data:
        return {
            "errors": state.errors + [{"agent": "Risk & Anomaly Agent", "message": "Missing upstream analysis or data."}]
        }
        
    try:
        # Layer A: Deterministic Rules
        rule_signals = evaluate_rules(state.financial_analysis, state.run_id)
        
        # Layer B: Anomaly Detection
        anomaly_signals = detect_market_anomalies(state.market_data.prices, state.run_id)
        
        all_signals = rule_signals + anomaly_signals
        
        # Calculate Score
        score, level = calculate_risk_score(all_signals)
        
        explanation = f"La puntuación de riesgo es {score} ({level}). "
        if all_signals:
            explanation += f"Impulsada por {len(all_signals)} señales activas."
        else:
            explanation += "No se detectaron señales de riesgo significativas."
            
        risk_analysis = RiskAnalysis(
            score=score,
            level=level,
            signals=all_signals,
            missing_data=[], # Could populate if data is missing
            limitations="La puntuación se basa en umbrales académicos configurables, no en límites regulatorios. El bosque de aislamiento se limita a series temporales.",
            explanation=explanation
        )
        
        return {
            "risk_analysis": risk_analysis
        }
    except Exception as e:
        return {
            "errors": state.errors + [{"agent": "Risk & Anomaly Agent", "message": str(e)}]
        }
