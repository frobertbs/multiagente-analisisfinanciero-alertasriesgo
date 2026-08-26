from typing import List, Optional
import math
from app.domain.models import FinancialPeriod, PriceBar, MetricResult

def _safe_divide(numerator: Optional[float], denominator: Optional[float]) -> Optional[float]:
    if numerator is None or denominator is None or denominator == 0:
        return None
    return numerator / denominator

def calculate_financial_metrics(periods: List[FinancialPeriod]) -> List[MetricResult]:
    # Sort periods just in case
    sorted_periods = sorted(periods, key=lambda x: x.period)
    metrics = []
    
    for i, current in enumerate(sorted_periods):
        period_str = current.period
        
        # 1. EBITDA Margin
        val = _safe_divide(current.ebitda, current.revenue)
        metrics.append(MetricResult(
            metric_name="ebitda_margin",
            value=val,
            unit="ratio",
            period=period_str,
            source_fields=["ebitda", "revenue"],
            calculation="ebitda / revenue",
            quality="available" if val is not None else "not_available"
        ))
        
        # 2. Net Margin
        val = _safe_divide(current.net_income, current.revenue)
        metrics.append(MetricResult(
            metric_name="net_margin",
            value=val,
            unit="ratio",
            period=period_str,
            source_fields=["net_income", "revenue"],
            calculation="net_income / revenue",
            quality="available" if val is not None else "not_available"
        ))
        
        # 3. ROA (Return on Assets)
        val = _safe_divide(current.net_income, current.total_assets)
        metrics.append(MetricResult(
            metric_name="roa",
            value=val,
            unit="ratio",
            period=period_str,
            source_fields=["net_income", "total_assets"],
            calculation="net_income / total_assets",
            quality="available" if val is not None else "not_available"
        ))
        
        # 4. ROE (Return on Equity)
        val = _safe_divide(current.net_income, current.total_equity)
        metrics.append(MetricResult(
            metric_name="roe",
            value=val,
            unit="ratio",
            period=period_str,
            source_fields=["net_income", "total_equity"],
            calculation="net_income / total_equity",
            quality="available" if val is not None else "not_available"
        ))
        
        # 5. Leverage Ratio (Total Debt / Total Equity)
        val = _safe_divide(current.total_debt, current.total_equity)
        metrics.append(MetricResult(
            metric_name="leverage_ratio",
            value=val,
            unit="ratio",
            period=period_str,
            source_fields=["total_debt", "total_equity"],
            calculation="total_debt / total_equity",
            quality="available" if val is not None else "not_available"
        ))
        
        # 6. Net Debt / EBITDA
        val = _safe_divide(current.net_debt, current.ebitda)
        metrics.append(MetricResult(
            metric_name="net_debt_to_ebitda",
            value=val,
            unit="ratio",
            period=period_str,
            source_fields=["net_debt", "ebitda"],
            calculation="net_debt / ebitda",
            quality="available" if val is not None else "not_available"
        ))
        
        # 7. Current Ratio
        val = _safe_divide(current.current_assets, current.current_liabilities)
        metrics.append(MetricResult(
            metric_name="current_ratio",
            value=val,
            unit="ratio",
            period=period_str,
            source_fields=["current_assets", "current_liabilities"],
            calculation="current_assets / current_liabilities",
            quality="available" if val is not None else "not_available"
        ))
        
        # 8. Interest Coverage
        val = _safe_divide(current.ebitda, current.interest_expense)
        metrics.append(MetricResult(
            metric_name="interest_coverage",
            value=val,
            unit="ratio",
            period=period_str,
            source_fields=["ebitda", "interest_expense"],
            calculation="ebitda / interest_expense",
            quality="available" if val is not None else "not_available"
        ))
        
        # Growth metrics (requires previous period)
        if i > 0:
            prev = sorted_periods[i-1]
            
            # Revenue Growth
            val = _safe_divide(current.revenue - prev.revenue if current.revenue is not None and prev.revenue is not None else None, prev.revenue)
            metrics.append(MetricResult(
                metric_name="revenue_growth",
                value=val,
                unit="ratio",
                period=period_str,
                source_fields=["revenue_current", "revenue_prev"],
                calculation="(revenue_current - revenue_prev) / revenue_prev",
                quality="available" if val is not None else "not_available"
            ))
            
            # EBITDA Growth
            val = _safe_divide(current.ebitda - prev.ebitda if current.ebitda is not None and prev.ebitda is not None else None, prev.ebitda)
            metrics.append(MetricResult(
                metric_name="ebitda_growth",
                value=val,
                unit="ratio",
                period=period_str,
                source_fields=["ebitda_current", "ebitda_prev"],
                calculation="(ebitda_current - ebitda_prev) / ebitda_prev",
                quality="available" if val is not None else "not_available"
            ))
            
            # Cash Growth
            val = _safe_divide(current.cash - prev.cash if current.cash is not None and prev.cash is not None else None, prev.cash)
            metrics.append(MetricResult(
                metric_name="cash_growth",
                value=val,
                unit="ratio",
                period=period_str,
                source_fields=["cash_current", "cash_prev"],
                calculation="(cash_current - cash_prev) / cash_prev",
                quality="available" if val is not None else "not_available"
            ))

    return metrics

def calculate_market_metrics(prices: List[PriceBar]) -> List[MetricResult]:
    if not prices:
        return []
    
    # Sort prices by date
    sorted_prices = sorted(prices, key=lambda x: x.date)
    period_str = f"{sorted_prices[0].date.isoformat()} to {sorted_prices[-1].date.isoformat()}"
    
    metrics = []
    
    # Cumulative return
    start_price = sorted_prices[0].close
    end_price = sorted_prices[-1].close
    cum_return = (end_price - start_price) / start_price if start_price > 0 else None
    
    metrics.append(MetricResult(
        metric_name="cumulative_return",
        value=cum_return,
        unit="ratio",
        period=period_str,
        source_fields=["close_start", "close_end"],
        calculation="(close_end - close_start) / close_start",
        quality="available" if cum_return is not None else "not_available"
    ))
    
    # Max Drawdown
    max_price = sorted_prices[0].close
    max_dd = 0.0
    for p in sorted_prices:
        if p.close > max_price:
            max_price = p.close
        dd = (max_price - p.close) / max_price if max_price > 0 else 0
        if dd > max_dd:
            max_dd = dd
            
    metrics.append(MetricResult(
        metric_name="max_drawdown",
        value=max_dd,
        unit="ratio",
        period=period_str,
        source_fields=["close"],
        calculation="max((peak - trough) / peak)",
        quality="available"
    ))
    
    # Historical Volatility (annualized, assuming daily prices)
    if len(sorted_prices) > 1:
        returns = []
        for i in range(1, len(sorted_prices)):
            prev = sorted_prices[i-1].close
            curr = sorted_prices[i].close
            if prev > 0:
                returns.append((curr - prev) / prev)
                
        if returns:
            mean_return = sum(returns) / len(returns)
            variance = sum((r - mean_return)**2 for r in returns) / (len(returns) - 1)
            daily_volatility = math.sqrt(variance)
            annual_volatility = daily_volatility * math.sqrt(252) # Assuming 252 trading days
            
            metrics.append(MetricResult(
                metric_name="historical_volatility",
                value=annual_volatility,
                unit="ratio",
                period=period_str,
                source_fields=["close"],
                calculation="stdev(daily_returns) * sqrt(252)",
                quality="available"
            ))
            
    return metrics
