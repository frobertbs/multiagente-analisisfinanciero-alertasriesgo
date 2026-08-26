from datetime import datetime, date
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field

class SourceRecord(BaseModel):
    source_name: str
    url: Optional[str] = None
    retrieval_date: datetime
    description: str

class FinancialPeriod(BaseModel):
    period: str
    revenue: Optional[float] = None
    ebitda: Optional[float] = None
    net_income: Optional[float] = None
    total_assets: Optional[float] = None
    total_equity: Optional[float] = None
    total_debt: Optional[float] = None
    net_debt: Optional[float] = None
    current_assets: Optional[float] = None
    current_liabilities: Optional[float] = None
    interest_expense: Optional[float] = None
    cash: Optional[float] = None

class CompanyData(BaseModel):
    ticker: str
    name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None

class PriceBar(BaseModel):
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int

class FinancialData(BaseModel):
    company: CompanyData
    periods: List[FinancialPeriod]

class MarketData(BaseModel):
    prices: List[PriceBar]

class NewsItem(BaseModel):
    headline: str
    source: str
    date: datetime
    url: Optional[str] = None
    summary: str
    event_type: Optional[str] = None

class MetricResult(BaseModel):
    metric_name: str
    value: Optional[float]
    unit: str
    period: str
    source_fields: List[str]
    calculation: str
    quality: str

class FinancialAnalysis(BaseModel):
    metrics: List[MetricResult]

class RiskSignal(BaseModel):
    signal_id: str
    category: str
    severity: str
    title: str
    description: str
    observed_value: Optional[float]
    threshold: Optional[float]
    period: Optional[str] = None
    evidence: List[str]
    confidence: float
    action: str

class RiskAnalysis(BaseModel):
    score: float
    level: str
    signals: List[RiskSignal]
    missing_data: List[str]
    limitations: str
    explanation: str

class ExecutiveReport(BaseModel):
    executive_summary: str
    risk_level: str
    risk_score: float
    key_findings: List[str]
    risk_alerts: List[str]
    positive_signals: List[str]
    recommended_review_actions: List[str]
    data_quality_notes: List[str]
    sources: List[str]
    disclaimer: str

class WarningItem(BaseModel):
    agent: str
    message: str

class ErrorItem(BaseModel):
    agent: str
    message: str

class AgentEvent(BaseModel):
    run_id: str
    agent_name: str
    event_type: str
    status: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    duration_ms: Optional[int] = None
    details: Optional[Dict[str, Any]] = None

class AnalysisState(BaseModel):
    run_id: str
    ticker: str
    company_name: Optional[str] = None
    analysis_period: str
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "pending"
    source_records: List[SourceRecord] = Field(default_factory=list)
    financial_data: Optional[FinancialData] = None
    market_data: Optional[MarketData] = None
    news_data: List[NewsItem] = Field(default_factory=list)
    financial_analysis: Optional[FinancialAnalysis] = None
    risk_analysis: Optional[RiskAnalysis] = None
    report: Optional[ExecutiveReport] = None
    warnings: List[WarningItem] = Field(default_factory=list)
    errors: List[ErrorItem] = Field(default_factory=list)
    agent_events: List[AgentEvent] = Field(default_factory=list)
