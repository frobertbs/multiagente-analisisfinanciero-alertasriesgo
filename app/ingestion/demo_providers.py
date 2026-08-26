import json
import os
from typing import List
from datetime import date, datetime
from app.domain.models import CompanyData, FinancialPeriod, PriceBar, NewsItem
from app.ingestion.providers import MarketDataProvider, NewsProvider

class DemoMarketDataProvider(MarketDataProvider):
    def __init__(self, data_dir: str = "data/demo"):
        self.data_dir = data_dir

    def _load_fixture(self, ticker: str) -> dict:
        filepath = os.path.join(self.data_dir, f"{ticker}.json")
        if not os.path.exists(filepath):
            raise ValueError(f"Demo data for {ticker} not found.")
        with open(filepath, 'r') as f:
            return json.load(f)

    def get_company(self, ticker: str) -> CompanyData:
        data = self._load_fixture(ticker)
        return CompanyData(**data["company"])

    def get_financials(self, ticker: str) -> List[FinancialPeriod]:
        data = self._load_fixture(ticker)
        return [FinancialPeriod(**p) for p in data.get("financials", [])]

    def get_prices(self, ticker: str, start: date, end: date) -> List[PriceBar]:
        data = self._load_fixture(ticker)
        prices = []
        for p in data.get("market_data", []):
            p_date = date.fromisoformat(p["date"])
            if start <= p_date <= end:
                prices.append(PriceBar(**p))
        return prices

class DemoNewsProvider(NewsProvider):
    def __init__(self, data_dir: str = "data/demo"):
        self.data_dir = data_dir

    def _load_fixture(self, ticker: str) -> dict:
        filepath = os.path.join(self.data_dir, f"{ticker}.json")
        if not os.path.exists(filepath):
            raise ValueError(f"Demo data for {ticker} not found.")
        with open(filepath, 'r') as f:
            return json.load(f)

    def search(self, ticker: str, start: date, end: date) -> List[NewsItem]:
        data = self._load_fixture(ticker)
        news = []
        for n in data.get("news", []):
            n_date = datetime.fromisoformat(n["date"]).date()
            if start <= n_date <= end:
                news.append(NewsItem(**n))
        return news
