from typing import Protocol, List
from datetime import date
from app.domain.models import CompanyData, FinancialPeriod, PriceBar, NewsItem

class MarketDataProvider(Protocol):
    def get_company(self, ticker: str) -> CompanyData:
        ...
    def get_financials(self, ticker: str) -> List[FinancialPeriod]:
        ...
    def get_prices(self, ticker: str, start: date, end: date) -> List[PriceBar]:
        ...

class NewsProvider(Protocol):
    def search(self, ticker: str, start: date, end: date) -> List[NewsItem]:
        ...
