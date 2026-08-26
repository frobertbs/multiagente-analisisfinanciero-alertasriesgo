from datetime import date, timedelta
from typing import Dict, Any
from app.domain.models import AnalysisState, SourceRecord, FinancialData, MarketData
from app.ingestion.demo_providers import DemoMarketDataProvider, DemoNewsProvider
from app.ingestion.real_providers import YFinanceDataProvider, YFinanceNewsProvider

def ingest_data_agent(state: AnalysisState) -> Dict[str, Any]:
    print(f"--- Ingesting data for {state.ticker} ---")
    
    is_demo = state.ticker.startswith("DEMO_")
    
    if is_demo:
        market_provider = DemoMarketDataProvider()
        news_provider = DemoNewsProvider()
        source_name = "Demo Data Provider"
    else:
        market_provider = YFinanceDataProvider()
        news_provider = YFinanceNewsProvider()
        source_name = "Yahoo Finance"
        
    # Calculate period
    end_date = date.today()
    if state.analysis_period == "1M":
        start_date = end_date - timedelta(days=30)
    elif state.analysis_period == "3M":
        start_date = end_date - timedelta(days=90)
    elif state.analysis_period == "6M":
        start_date = end_date - timedelta(days=180)
    else: # 1Y default
        start_date = end_date - timedelta(days=365)
    
    try:
        # Get Company
        company = market_provider.get_company(state.ticker)
        
        # Get Financials
        periods = market_provider.get_financials(state.ticker)
        financial_data = FinancialData(company=company, periods=periods)
        
        # Get Prices
        prices = market_provider.get_prices(state.ticker, start_date, end_date)
        market_data = MarketData(prices=prices)
        
        # Get News
        news_data = news_provider.search(state.ticker, start_date, end_date)
        
        source_records = state.source_records + [
            SourceRecord(
                source_name=source_name,
                retrieval_date=state.requested_at,
                description=f"Market and financial data for {state.analysis_period}"
            )
        ]
        
        return {
            "company_name": company.name,
            "financial_data": financial_data,
            "market_data": market_data,
            "news_data": news_data,
            "source_records": source_records
        }
        
    except Exception as e:
        return {
            "errors": state.errors + [{"agent": "Data Ingestion Agent", "message": f"Failed to ingest data: {str(e)}"}]
        }
