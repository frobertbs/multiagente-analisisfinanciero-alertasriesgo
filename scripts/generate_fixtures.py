import json
import os
from datetime import datetime, timedelta, date

def generate_financial_periods(profile: str):
    periods = []
    years = ["2022", "2023", "2024"]
    if profile == "STBL":
        # Stable growth
        for i, year in enumerate(years):
            rev = 1000 + (i * 50)
            ebitda = 200 + (i * 15)
            net_income = 100 + (i * 10)
            debt = 300
            periods.append({
                "period": year,
                "revenue": rev,
                "ebitda": ebitda,
                "net_income": net_income,
                "total_assets": 1500,
                "total_equity": 800,
                "total_debt": debt,
                "net_debt": debt - 150,
                "current_assets": 400,
                "current_liabilities": 200,
                "interest_expense": 15,
                "cash": 150 + (i * 10)
            })
    elif profile == "LEVR":
        # Deterioration and high leverage
        for i, year in enumerate(years):
            rev = 1000 - (i * 50)
            ebitda = 200 - (i * 30)
            net_income = 100 - (i * 20)
            debt = 300 + (i * 200)
            periods.append({
                "period": year,
                "revenue": rev,
                "ebitda": ebitda,
                "net_income": net_income,
                "total_assets": 1500,
                "total_equity": 800 - (i * 50),
                "total_debt": debt,
                "net_debt": debt - 50,
                "current_assets": 300 - (i * 20),
                "current_liabilities": 200 + (i * 50),
                "interest_expense": 15 + (i * 10),
                "cash": 50 - (i * 5)
            })
    elif profile == "VOLT":
        # Erratic
        for i, year in enumerate(years):
            rev = 1000 + (-200 if i == 1 else 300)
            ebitda = 200 + (-100 if i == 1 else 150)
            net_income = 100 + (-50 if i == 1 else 70)
            debt = 400
            periods.append({
                "period": year,
                "revenue": rev,
                "ebitda": ebitda,
                "net_income": net_income,
                "total_assets": 1500,
                "total_equity": 800,
                "total_debt": debt,
                "net_debt": debt - 100,
                "current_assets": 400,
                "current_liabilities": 300,
                "interest_expense": 20,
                "cash": 100
            })
    return periods

def generate_market_data(profile: str):
    prices = []
    base_price = 100.0
    current_date = date.today() - timedelta(days=252)
    import random
    random.seed(42 if profile == "STBL" else (43 if profile == "LEVR" else 44))
    
    volatility = 0.01
    if profile == "VOLT": volatility = 0.05
    
    for i in range(252):
        if current_date.weekday() < 5:  # Trading days
            change = random.normalvariate(0, volatility)
            if profile == "LEVR":
                change -= 0.001 # Downward drift
            base_price = base_price * (1 + change)
            
            prices.append({
                "date": current_date.isoformat(),
                "open": base_price,
                "high": base_price * 1.01,
                "low": base_price * 0.99,
                "close": base_price,
                "volume": int(1000000 * (1 + abs(random.normalvariate(0, 0.2))))
            })
        current_date += timedelta(days=1)
    return prices

def generate_news(profile: str):
    if profile == "STBL":
        return [
            {"headline": "Steady Growth Continues", "source": "DemoNews", "date": datetime.utcnow().isoformat(), "summary": "Company announces steady quarterly results.", "event_type": "earnings"}
        ]
    elif profile == "LEVR":
        return [
            {"headline": "Debt Concerns Mount", "source": "DemoNews", "date": datetime.utcnow().isoformat(), "summary": "Analysts warn about increasing leverage ratios.", "event_type": "debt"},
            {"headline": "Cash Flow Squeeze", "source": "DemoNews", "date": (datetime.utcnow() - timedelta(days=5)).isoformat(), "summary": "Working capital pressure reported.", "event_type": "operations"}
        ]
    elif profile == "VOLT":
        return [
            {"headline": "Massive Price Swing Follows Earnings Miss", "source": "DemoNews", "date": datetime.utcnow().isoformat(), "summary": "Stock plummets 15% before recovering slightly.", "event_type": "market"},
            {"headline": "CEO Resigns Unexpectedly", "source": "DemoNews", "date": (datetime.utcnow() - timedelta(days=10)).isoformat(), "summary": "Leadership changes cause uncertainty.", "event_type": "management"}
        ]
    return []

def main():
    os.makedirs("data/demo", exist_ok=True)
    profiles = [
        ("DEMO_STBL", "Stable Corp"),
        ("DEMO_LEVR", "Leverage Inc"),
        ("DEMO_VOLT", "Volatile Energy")
    ]
    
    for ticker, name in profiles:
        profile_type = ticker.split("_")[1]
        data = {
            "company": {
                "ticker": ticker,
                "name": name,
                "sector": "Demo Sector",
                "industry": "Demo Industry"
            },
            "financials": generate_financial_periods(profile_type),
            "market_data": generate_market_data(profile_type),
            "news": generate_news(profile_type)
        }
        with open(f"data/demo/{ticker}.json", "w") as f:
            json.dump(data, f, indent=2)
            print(f"Generated {ticker}.json")

if __name__ == "__main__":
    main()
