import pandas as pd
from sklearn.ensemble import IsolationForest
from typing import List, Optional
from app.domain.models import PriceBar, RiskSignal

def detect_market_anomalies(prices: List[PriceBar], run_id: str) -> List[RiskSignal]:
    if len(prices) < 50:
        # Not enough observations for a robust isolation forest
        return []

    # Convert to DataFrame
    df = pd.DataFrame([{
        "date": p.date,
        "close": p.close,
        "volume": p.volume
    } for p in prices])
    
    # Calculate daily returns and rolling volatility
    df['return'] = df['close'].pct_change()
    df['rolling_volatility'] = df['return'].rolling(window=10).std()
    
    # Drop NaNs
    df_clean = df.dropna().copy()
    
    if len(df_clean) < 50:
        return []
        
    features = df_clean[['return', 'volume', 'rolling_volatility']]
    
    # Isolation Forest
    # Contamination set to 0.05 (5% anomalies)
    model = IsolationForest(contamination=0.05, random_state=42)
    df_clean['anomaly'] = model.fit_predict(features)
    
    # -1 means anomaly
    anomalies = df_clean[df_clean['anomaly'] == -1]
    
    signals = []
    # If there are recent anomalies (in the last 10 trading days), generate a signal
    recent_anomalies = anomalies.tail(10)
    
    if not recent_anomalies.empty:
        signals.append(RiskSignal(
            signal_id="market_anomaly_detected",
            category="market_behavior",
            severity="medium", # Unusual behavior signal, not necessarily critical
            title="Comportamiento Inusual del Mercado",
            description=f"Isolation Forest detectó {len(recent_anomalies)} días de negociación anómalos en el período reciente basándose en rendimientos, volumen y volatilidad.",
            observed_value=float(len(recent_anomalies)),
            threshold=None,
            period="reciente",
            evidence=["daily_returns", "volume", "rolling_volatility"],
            confidence=0.8,
            action="Revisar eventos recientes del mercado y noticias en busca de impulsores contextuales."
        ))
        
    return signals
