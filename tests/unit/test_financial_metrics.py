import pytest
from app.domain.models import FinancialPeriod
from app.analytics.financial_metrics import calculate_financial_metrics, _safe_divide

def test_safe_divide():
    assert _safe_divide(10, 2) == 5.0
    assert _safe_divide(10, 0) is None
    assert _safe_divide(None, 2) is None
    assert _safe_divide(10, None) is None

def test_calculate_financial_metrics():
    periods = [
        FinancialPeriod(
            period="2023",
            revenue=1000,
            ebitda=200,
            net_income=100,
            total_assets=1000,
            total_equity=500,
            total_debt=300,
            net_debt=200,
            current_assets=400,
            current_liabilities=200,
            interest_expense=20,
            cash=100
        )
    ]
    
    metrics = calculate_financial_metrics(periods)
    
    metrics_map = {m.metric_name: m.value for m in metrics}
    
    assert metrics_map["ebitda_margin"] == 0.2
    assert metrics_map["net_margin"] == 0.1
    assert metrics_map["roa"] == 0.1
    assert metrics_map["roe"] == 0.2
    assert metrics_map["leverage_ratio"] == 0.6
    assert metrics_map["net_debt_to_ebitda"] == 1.0
    assert metrics_map["current_ratio"] == 2.0
    assert metrics_map["interest_coverage"] == 10.0
