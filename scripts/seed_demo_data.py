import sys
import os
from datetime import date, timedelta

# Add the project root to python path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.persistence.database import init_db, SessionLocal, Company, FinancialPeriod, MarketPrice, NewsItem
from app.ingestion.demo_providers import DemoMarketDataProvider, DemoNewsProvider

def seed():
    init_db()
    db = SessionLocal()
    
    market_provider = DemoMarketDataProvider()
    news_provider = DemoNewsProvider()
    
    tickers = ["DEMO_STBL", "DEMO_LEVR", "DEMO_VOLT"]
    
    start_date = date.today() - timedelta(days=365)
    end_date = date.today()

    for ticker in tickers:
        print(f"Seeding {ticker}...")
        
        # Check if already seeded
        if db.query(Company).filter(Company.ticker == ticker).first():
            print(f"  {ticker} already exists. Skipping.")
            continue
            
        company_data = market_provider.get_company(ticker)
        company = Company(
            ticker=company_data.ticker,
            name=company_data.name,
            sector=company_data.sector,
            industry=company_data.industry,
            description=company_data.description
        )
        db.add(company)
        db.commit()

        financials = market_provider.get_financials(ticker)
        for f in financials:
            fp = FinancialPeriod(
                ticker=ticker,
                period=f.period,
                revenue=f.revenue,
                ebitda=f.ebitda,
                net_income=f.net_income,
                total_assets=f.total_assets,
                total_equity=f.total_equity,
                total_debt=f.total_debt,
                net_debt=f.net_debt,
                current_assets=f.current_assets,
                current_liabilities=f.current_liabilities,
                interest_expense=f.interest_expense,
                cash=f.cash
            )
            db.add(fp)
            
        prices = market_provider.get_prices(ticker, start_date, end_date)
        for p in prices:
            mp = MarketPrice(
                ticker=ticker,
                date=p.date, # In production might need datetime conversion if schema expects datetime
                open=p.open,
                high=p.high,
                low=p.low,
                close=p.close,
                volume=p.volume
            )
            db.add(mp)
            
        news = news_provider.search(ticker, start_date, end_date)
        for n in news:
            ni = NewsItem(
                ticker=ticker,
                headline=n.headline,
                source=n.source,
                date=n.date,
                url=n.url,
                summary=n.summary,
                event_type=n.event_type
            )
            db.add(ni)
            
        db.commit()
        print(f"  Done seeding {ticker}")
        
    db.close()
    print("Database seeding complete.")

if __name__ == "__main__":
    seed()
