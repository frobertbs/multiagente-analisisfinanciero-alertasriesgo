import yaml
from typing import List, Dict, Any
from app.domain.models import FinancialAnalysis, RiskSignal

def load_rules(config_path: str = "configs/risk_rules.yaml") -> Dict[str, Any]:
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def evaluate_rules(analysis: FinancialAnalysis, run_id: str, config_path: str = "configs/risk_rules.yaml") -> List[RiskSignal]:
    config = load_rules(config_path)
    rules = config.get('rules', {})
    signals = []
    
    # Create a lookup for metrics
    # If there are multiple periods, we evaluate against the latest period
    latest_metrics = {}
    for m in analysis.metrics:
        # Assuming the list is ordered or we just take the last seen for a metric
        latest_metrics[m.metric_name] = m
        
    for rule_id, rule_def in rules.items():
        if not rule_def.get('enabled', False):
            continue
            
        metric_name = rule_def['metric']
        if metric_name not in latest_metrics:
            continue
            
        metric = latest_metrics[metric_name]
        if metric.value is None or metric.quality != "available":
            continue
            
        val = metric.value
        threshold = rule_def['threshold']
        direction = rule_def['direction']
        
        triggered = False
        if direction == 'greater_than' and val > threshold:
            triggered = True
        elif direction == 'lower_than' and val < threshold:
            triggered = True
            
        if triggered:
            signals.append(RiskSignal(
                signal_id=rule_id,
                category=metric_name,
                severity=rule_def['severity'],
                title=f"Regla Activada: {rule_id}",
                description=rule_def['description'],
                observed_value=val,
                threshold=threshold,
                period=metric.period,
                evidence=[metric_name],
                confidence=1.0,
                action=f"Revisar tendencias de {metric_name}."
            ))
            
    return signals

def calculate_risk_score(signals: List[RiskSignal], config_path: str = "configs/risk_rules.yaml") -> tuple[float, str]:
    config = load_rules(config_path)
    weights = config.get('score_weights', {})
    
    total_score = 0.0
    for s in signals:
        total_score += weights.get(s.severity, 0)
        
    # Cap score at 100
    score = min(100.0, total_score)
    
    # Determine level based on the bands in the spec
    # low: 0–29; moderate: 30–59; high: 60–79; critical: 80–100.
    if score < 30:
        level = "low"
    elif score < 60:
        level = "moderate"
    elif score < 80:
        level = "high"
    else:
        level = "critical"
        
    return score, level
