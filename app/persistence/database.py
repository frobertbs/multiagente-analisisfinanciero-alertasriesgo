import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()

# ----------------- Domain Entities -----------------

class Company(Base):
    __tablename__ = 'companies'
    ticker = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    sector = Column(String)
    industry = Column(String)
    description = Column(Text)
    
    financial_periods = relationship("FinancialPeriod", back_populates="company")
    market_prices = relationship("MarketPrice", back_populates="company")
    news_items = relationship("NewsItem", back_populates="company")

class FinancialPeriod(Base):
    __tablename__ = 'financial_periods'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String, ForeignKey('companies.ticker'))
    period = Column(String, nullable=False)  # e.g., '2023', 'Q1-2023'
    revenue = Column(Float)
    ebitda = Column(Float)
    net_income = Column(Float)
    total_assets = Column(Float)
    total_equity = Column(Float)
    total_debt = Column(Float)
    net_debt = Column(Float)
    current_assets = Column(Float)
    current_liabilities = Column(Float)
    interest_expense = Column(Float)
    cash = Column(Float)

    company = relationship("Company", back_populates="financial_periods")

class MarketPrice(Base):
    __tablename__ = 'market_prices'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String, ForeignKey('companies.ticker'))
    date = Column(DateTime, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)

    company = relationship("Company", back_populates="market_prices")

class NewsItem(Base):
    __tablename__ = 'news_items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String, ForeignKey('companies.ticker'))
    headline = Column(String, nullable=False)
    source = Column(String)
    date = Column(DateTime)
    url = Column(String)
    summary = Column(Text)
    event_type = Column(String)

    company = relationship("Company", back_populates="news_items")

# ----------------- Execution Trace Entities -----------------

class AnalysisRun(Base):
    __tablename__ = 'analysis_runs'
    run_id = Column(String, primary_key=True)
    ticker = Column(String, index=True)
    analysis_period = Column(String)
    status = Column(String, default="pending")
    requested_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    risk_score = Column(Float)
    risk_level = Column(String)

    events = relationship("AgentEvent", back_populates="run")
    signals = relationship("RiskSignal", back_populates="run")

class AgentEvent(Base):
    __tablename__ = 'agent_events'
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, ForeignKey('analysis_runs.run_id'))
    agent_name = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    duration_ms = Column(Integer)
    details = Column(Text)  # JSON string

    run = relationship("AnalysisRun", back_populates="events")

class RiskSignal(Base):
    __tablename__ = 'risk_signals'
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, ForeignKey('analysis_runs.run_id'))
    signal_id = Column(String, nullable=False)
    category = Column(String)
    severity = Column(String)
    title = Column(String)
    description = Column(Text)
    observed_value = Column(Float)
    threshold = Column(Float)
    
    run = relationship("AnalysisRun", back_populates="signals")

class Report(Base):
    __tablename__ = 'reports'
    run_id = Column(String, ForeignKey('analysis_runs.run_id'), primary_key=True)
    content = Column(Text)  # JSON string of ExecutiveReport
    generated_at = Column(DateTime, default=datetime.utcnow)

# ----------------- Database Setup -----------------

# Get database URL from environment, default to local sqlite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/demo/financial_app.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
