import yfinance as yf
from datetime import date, datetime
from typing import List
from app.domain.models import CompanyData, FinancialPeriod, PriceBar, NewsItem
from app.ingestion.providers import MarketDataProvider, NewsProvider

class YFinanceDataProvider(MarketDataProvider):
    def get_company(self, ticker: str) -> CompanyData:
        stock = yf.Ticker(ticker)
        info = stock.info
        return CompanyData(
            ticker=ticker,
            name=info.get("shortName", ticker),
            sector=info.get("sector"),
            industry=info.get("industry"),
            description=info.get("longBusinessSummary")
        )

    def get_financials(self, ticker: str) -> List[FinancialPeriod]:
        stock = yf.Ticker(ticker)
        
        # yfinance financials (income statement), balance_sheet, cashflow
        try:
            inc = stock.financials
            bs = stock.balance_sheet
            cf = stock.cashflow
        except Exception:
            return []
            
        periods = []
        if inc is not None and not inc.empty:
            # Iterate over the columns (which are dates)
            for date_col in inc.columns:
                try:
                    # Helper to safely get values
                    def get_val(df, field, default=None):
                        try:
                            val = df.loc[field, date_col]
                            import pandas as pd
                            if pd.isna(val): return default
                            return float(val)
                        except KeyError:
                            return default

                    rev = get_val(inc, "Total Revenue")
                    ebitda = get_val(inc, "EBITDA") or get_val(inc, "Normalized EBITDA")
                    net_income = get_val(inc, "Net Income")
                    interest_expense = get_val(inc, "Interest Expense")
                    
                    total_assets = get_val(bs, "Total Assets") if bs is not None else None
                    total_equity = get_val(bs, "Stockholders Equity") if bs is not None else None
                    total_debt = get_val(bs, "Total Debt") if bs is not None else None
                    cash = get_val(bs, "Cash And Cash Equivalents") if bs is not None else None
                    current_assets = get_val(bs, "Current Assets") if bs is not None else None
                    current_liabilities = get_val(bs, "Current Liabilities") if bs is not None else None
                    
                    net_debt = None
                    if total_debt is not None and cash is not None:
                        net_debt = total_debt - cash

                    periods.append(FinancialPeriod(
                        period=str(date_col.year), # Using year as period identifier for simplicity
                        revenue=rev,
                        ebitda=ebitda,
                        net_income=net_income,
                        total_assets=total_assets,
                        total_equity=total_equity,
                        total_debt=total_debt,
                        net_debt=net_debt,
                        current_assets=current_assets,
                        current_liabilities=current_liabilities,
                        interest_expense=interest_expense,
                        cash=cash
                    ))
                except Exception as e:
                    print(f"Error parsing financial column {date_col} for {ticker}: {e}")
                    pass
                    
        return sorted(periods, key=lambda x: x.period)

    def get_prices(self, ticker: str, start: date, end: date) -> List[PriceBar]:
        stock = yf.Ticker(ticker)
        df = stock.history(start=start.strftime('%Y-%m-%d'), end=end.strftime('%Y-%m-%d'))
        
        prices = []
        for idx, row in df.iterrows():
            prices.append(PriceBar(
                date=idx.date(),
                open=float(row['Open']),
                high=float(row['High']),
                low=float(row['Low']),
                close=float(row['Close']),
                volume=int(row['Volume'])
            ))
        return prices

class YFinanceNewsProvider(NewsProvider):
    def search(self, ticker: str, start: date, end: date) -> List[NewsItem]:
        stock = yf.Ticker(ticker)
        raw_news = stock.news
        news_items = []
        for n in raw_news:
            try:
                # yfinance news timestamp is unix epoch
                dt = datetime.fromtimestamp(n.get('providerPublishTime', 0))
                if start <= dt.date() <= end:
                    news_items.append(NewsItem(
                        headline=n.get('title', ''),
                        source=n.get('publisher', 'Yahoo Finance'),
                        date=dt,
                        url=n.get('link', ''),
                        summary=n.get('relatedTickers', str(ticker)), # yfinance API usually doesn't give a full summary in the base call
                        event_type="market"
                    ))
            except Exception:
                pass
        return news_items
