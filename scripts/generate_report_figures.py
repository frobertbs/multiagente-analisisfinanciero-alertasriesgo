import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd
import json

# Ensure docs/images directory exists
os.makedirs("docs/images", exist_ok=True)
os.environ["MPLCONFIGDIR"] = "/tmp"

# Set style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Helvetica, Arial, DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#CBD5E1'
plt.rcParams['axes.linewidth'] = 0.8

# -------------------------------------------------------------
# FIGURA 1: Arquitectura del Sistema Implementado
# -------------------------------------------------------------
def generate_fig1_architecture():
    fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
    ax.axis('off')
    
    # Title
    ax.text(0.5, 0.96, "Arquitectura del Sistema Multiagente Implementado", 
            fontsize=15, fontweight='bold', ha='center', color='#0F172A')
    ax.text(0.5, 0.92, "Estructura desacoplada por capas: Presentación, Servicio API, Orquestación, Analítica y Persistencia", 
            fontsize=10, fontstyle='italic', ha='center', color='#475569')

    # Draw Layers
    layers = [
        ("1. Capa de Presentación (Streamlit UI)", 0.82, "#EFF6FF", "#1E40AF", [
            "Interfaz interactiva de usuario (`app/ui/streamlit_app.py`)",
            "Configuración de Ticker (DEMO / Real Yahoo Finance) y Período (1M, 3M, 6M, 1Y)",
            "Polling reactivo, métrica global de riesgo, desglose de alertas y descarga JSON"
        ]),
        ("2. Capa de Servicio y API (FastAPI)", 0.65, "#F0FDF4", "#166534", [
            "Servidor REST (`app/api/main.py`, `app/api/endpoints.py`) con Uvicorn",
            "Endpoints: POST /analyses, GET /analyses/{id}, GET .../report, GET .../events",
            "Ejecución asíncrona mediante BackgroundTasks de FastAPI"
        ]),
        ("3. Capa de Orquestación Multiagente (LangGraph)", 0.48, "#FAF5FF", "#6B21A8", [
            "Grafo de estados dirigido (`StateGraph(AnalysisState)`) en `app/orchestration/graph.py`",
            "Wrapper con trazabilidad temporal y registro de eventos (`AgentEvent`) por agente",
            "Flujo: Data Ingestion -> Financial Analysis -> News Context -> Risk Anomaly -> Report Generator"
        ]),
        ("4. Capa Analítica y de Machine Learning", 0.31, "#FFFBEB", "#92400E", [
            "Métricas Financieras Deterministas (`financial_metrics.py`): 14 ratios y variaciones",
            "Motor de Reglas Configurable (`rule_engine.py` + `configs/risk_rules.yaml`)",
            "Detección de Anomalías (`anomaly_detection.py`): Isolation Forest (scikit-learn)",
            "Motor RAG (`rag_engine.py`): Vector store FAISS + OpenAI Embeddings"
        ]),
        ("5. Capa de Persistencia y Trazabilidad (SQLAlchemy / SQLite)", 0.14, "#F1F5F9", "#334155", [
            "Base de datos relacional (`app/persistence/database.py`): `financial_app.db`",
            "Tablas de Negocio: `companies`, `financial_periods`, `market_prices`, `news_items`",
            "Tablas de Trazabilidad: `analysis_runs`, `agent_events`, `risk_signals`, `reports`"
        ])
    ]

    for title, y, bg_color, border_color, items in layers:
        rect = patches.FancyBboxPatch((0.05, y - 0.06), 0.90, 0.12,
                                     boxstyle="round,pad=0.015,rounding_size=0.015",
                                     linewidth=1.5, edgecolor=border_color, facecolor=bg_color)
        ax.add_patch(rect)
        ax.text(0.07, y + 0.04, title, fontsize=11, fontweight='bold', color=border_color)
        for i, item in enumerate(items):
            ax.text(0.09, y + 0.012 - (i * 0.024), f"• {item}", fontsize=8.5, color='#1E293B')

    # Arrows between layers
    arrow_props = dict(arrowstyle="->", lw=2, color="#64748B")
    for y in [0.76, 0.59, 0.42, 0.25]:
        ax.annotate('', xy=(0.5, y - 0.02), xytext=(0.5, y + 0.005), arrowprops=arrow_props)

    plt.tight_layout()
    plt.savefig("docs/images/fig1_arquitectura_sistema.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated fig1_arquitectura_sistema.png")

# -------------------------------------------------------------
# FIGURA 2: Flujo de Ejecución Multiagente y StateGraph
# -------------------------------------------------------------
def generate_fig2_workflow():
    fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)
    ax.axis('off')
    
    ax.text(0.5, 0.96, "Flujo Secuencial de Agentes y Transición de Estados (LangGraph)", 
            fontsize=14, fontweight='bold', ha='center', color='#0F172A')
    ax.text(0.5, 0.92, "Evolución incremental del objeto de estado global `AnalysisState` a través del grafo", 
            fontsize=9.5, fontstyle='italic', ha='center', color='#475569')

    nodes = [
        ("1. Data Ingestion\nAgent", 0.10, "#DBEAFE", "#1D4ED8", "Ingesta de estados,\nprecios y noticias\n(Demo / YFinance)"),
        ("2. Financial Analysis\nAgent", 0.30, "#DCFCE7", "#15803D", "Cálculo de ratios\nfinancieros y métricas\nde mercado"),
        ("3. News & Context\nAgent", 0.50, "#FEF9C3", "#A16207", "Indexación RAG\nvectorial FAISS de\nnoticias recientes"),
        ("4. Risk & Anomaly\nAgent", 0.70, "#FFEDD5", "#C2410C", "Reglas deterministas\n+ Isolation Forest +\nPuntuación 0-100"),
        ("5. Report Generator\nAgent", 0.90, "#F3E8FF", "#7E22CE", "Generación de informe\nejecutivo estructurado\nJSON con LLM")
    ]

    for title, x, bg_color, border_color, desc in nodes:
        rect = patches.FancyBboxPatch((x - 0.08, 0.48), 0.16, 0.32,
                                     boxstyle="round,pad=0.015,rounding_size=0.015",
                                     linewidth=1.5, edgecolor=border_color, facecolor=bg_color)
        ax.add_patch(rect)
        ax.text(x, 0.73, title, fontsize=9.5, fontweight='bold', ha='center', va='center', color=border_color)
        ax.text(x, 0.57, desc, fontsize=8, ha='center', va='center', color='#1E293B')

    # Connecting arrows
    arrow_props = dict(arrowstyle="->", lw=2.5, color="#475569")
    for x in [0.18, 0.38, 0.58, 0.78]:
        ax.annotate('', xy=(x + 0.04, 0.64), xytext=(x, 0.64), arrowprops=arrow_props)

    # State evolution box below
    state_box = patches.FancyBboxPatch((0.03, 0.08), 0.94, 0.32,
                                      boxstyle="round,pad=0.015,rounding_size=0.015",
                                      linewidth=1.2, edgecolor="#94A3B8", facecolor="#F8FAFC")
    ax.add_patch(state_box)
    ax.text(0.05, 0.35, "Estructura del Estado Compartido (`AnalysisState` en Pydantic):", 
            fontsize=10, fontweight='bold', color='#0F172A')

    state_steps = [
        ("Entrada Inicial:", "run_id, ticker, analysis_period, requested_at, status='pending'"),
        ("Tras Ingestión:", "+ company_name, financial_data (periods), market_data (prices), news_data, source_records"),
        ("Tras Análisis:", "+ financial_analysis (ebitda_margin, leverage_ratio, current_ratio, interest_cov, ... 14 ratios)"),
        ("Tras Riesgo:", "+ risk_analysis (score [0-100], level ['low'|'moderate'|'high'|'critical'], signals [RiskSignal])"),
        ("Tras Informe:", "+ report (ExecutiveReport JSON), agent_events (duración_ms y estado por agente)")
    ]

    for i, (label, val) in enumerate(state_steps):
        ax.text(0.06, 0.30 - (i * 0.045), label, fontsize=8.5, fontweight='bold', color='#334155')
        ax.text(0.20, 0.30 - (i * 0.045), val, fontsize=8, fontfamily='monospace', color='#0369A1')

    plt.tight_layout()
    plt.savefig("docs/images/fig2_flujo_multiagente.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated fig2_flujo_multiagente.png")

# -------------------------------------------------------------
# FIGURA 3: Análisis Financiero Comparativo (DEMO_STBL vs DEMO_LEVR)
# -------------------------------------------------------------
def generate_fig3_financial_comparison():
    with open("data/demo/DEMO_STBL.json") as f:
        stbl = json.load(f)
    with open("data/demo/DEMO_LEVR.json") as f:
        levr = json.load(f)

    years = [p["period"] for p in stbl["financials"]]
    
    stbl_rev = [p["revenue"] for p in stbl["financials"]]
    levr_rev = [p["revenue"] for p in levr["financials"]]

    stbl_ebitda = [p["ebitda"] for p in stbl["financials"]]
    levr_ebitda = [p["ebitda"] for p in levr["financials"]]

    stbl_debt_ebitda = [p["net_debt"] / p["ebitda"] for p in stbl["financials"]]
    levr_debt_ebitda = [p["net_debt"] / p["ebitda"] for p in levr["financials"]]

    stbl_cr = [p["current_assets"] / p["current_liabilities"] for p in stbl["financials"]]
    levr_cr = [p["current_assets"] / p["current_liabilities"] for p in levr["financials"]]

    fig, axes = plt.subplots(2, 2, figsize=(11, 7.5), dpi=300)
    fig.suptitle("Comparativa de Indicadores Financieros: Perfil Estable (DEMO_STBL) vs Apalancado (DEMO_LEVR)\n[Datos Demo]", 
                 fontsize=13, fontweight='bold', color='#0F172A', y=0.98)

    # 1. Ingresos
    ax1 = axes[0, 0]
    ax1.plot(years, stbl_rev, 'o-', color='#059669', lw=2, label="DEMO_STBL (Crecimiento)")
    ax1.plot(years, levr_rev, 's--', color='#DC2626', lw=2, label="DEMO_LEVR (Deterioro)")
    ax1.set_title("Evolución de Ingresos (€ M)", fontsize=11, fontweight='bold', pad=8)
    ax1.set_ylabel("Ingresos (€)")
    ax1.legend(frameon=True, fontsize=8.5)
    ax1.grid(True, linestyle=':', alpha=0.6)

    # 2. EBITDA
    ax2 = axes[0, 1]
    ax2.plot(years, stbl_ebitda, 'o-', color='#059669', lw=2, label="DEMO_STBL")
    ax2.plot(years, levr_ebitda, 's--', color='#DC2626', lw=2, label="DEMO_LEVR")
    ax2.set_title("Evolución de EBITDA (€ M)", fontsize=11, fontweight='bold', pad=8)
    ax2.set_ylabel("EBITDA (€)")
    ax2.legend(frameon=True, fontsize=8.5)
    ax2.grid(True, linestyle=':', alpha=0.6)

    # 3. Deuda Neta / EBITDA
    ax3 = axes[1, 0]
    ax3.plot(years, stbl_debt_ebitda, 'o-', color='#059669', lw=2, label="DEMO_STBL (Bajo riesgo)")
    ax3.plot(years, levr_debt_ebitda, 's--', color='#DC2626', lw=2, label="DEMO_LEVR (Alto riesgo)")
    ax3.axhline(3.5, color='#B91C1C', linestyle=':', lw=1.5, label="Umbral Riesgo Alto (>3.5x)")
    ax3.set_title("Ratio Deuda Neta / EBITDA (Apalancamiento)", fontsize=11, fontweight='bold', pad=8)
    ax3.set_ylabel("Ratio (veces)")
    ax3.legend(frameon=True, fontsize=8.5)
    ax3.grid(True, linestyle=':', alpha=0.6)

    # 4. Current Ratio (Liquidez)
    ax4 = axes[1, 1]
    ax4.plot(years, stbl_cr, 'o-', color='#059669', lw=2, label="DEMO_STBL")
    ax4.plot(years, levr_cr, 's--', color='#DC2626', lw=2, label="DEMO_LEVR")
    ax4.axhline(1.0, color='#B91C1C', linestyle=':', lw=1.5, label="Umbral Liquidez Crítica (<1.0x)")
    ax4.set_title("Current Ratio (Liquidez a Corto Plazo)", fontsize=11, fontweight='bold', pad=8)
    ax4.set_ylabel("Ratio Corriente")
    ax4.legend(frameon=True, fontsize=8.5)
    ax4.grid(True, linestyle=':', alpha=0.6)

    plt.tight_layout()
    plt.subplots_adjust(top=0.90)
    plt.savefig("docs/images/fig3_analisis_financiero_comparativa.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated fig3_analisis_financiero_comparativa.png")

# -------------------------------------------------------------
# FIGURA 4: Detección de Anomalías con Isolation Forest
# -------------------------------------------------------------
def generate_fig4_anomaly_detection():
    from sklearn.ensemble import IsolationForest
    
    with open("data/demo/DEMO_LEVR.json") as f:
        data = json.load(f)
        
    prices = data["market_data"]
    df = pd.DataFrame(prices)
    df['date'] = pd.to_datetime(df['date'])
    df['return'] = df['close'].pct_change()
    df['rolling_volatility'] = df['return'].rolling(window=10).std()
    df_clean = df.dropna().copy()
    
    features = df_clean[['return', 'volume', 'rolling_volatility']]
    model = IsolationForest(contamination=0.05, random_state=42)
    df_clean['anomaly'] = model.fit_predict(features)
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(11, 8), dpi=300, sharex=True)
    fig.suptitle("Detección de Anomalías de Mercado con Isolation Forest (DEMO_LEVR)\n[Datos Demo]", 
                 fontsize=13, fontweight='bold', color='#0F172A', y=0.98)

    # 1. Precios de Cierre y Anomalías
    anomalies = df_clean[df_clean['anomaly'] == -1]

    ax1.plot(df_clean['date'], df_clean['close'], color='#2563EB', lw=1.5, label="Precio de Cierre (€)")
    ax1.scatter(anomalies['date'], anomalies['close'], color='#DC2626', s=45, zorder=5, 
                label=f"Anomalía Detectada (N={len(anomalies)})")
    ax1.set_title("Serie Temporal de Precios de Cierre", fontsize=10.5, fontweight='bold')
    ax1.set_ylabel("Precio (€)")
    ax1.legend(loc='upper right', frameon=True, fontsize=8.5)
    ax1.grid(True, linestyle=':', alpha=0.6)

    # 2. Rendimientos Diarios
    ax2.plot(df_clean['date'], df_clean['return'] * 100, color='#64748B', lw=1, label="Rendimiento Diario (%)")
    ax2.scatter(anomalies['date'], anomalies['return'] * 100, color='#DC2626', s=45, zorder=5)
    ax2.axhline(0, color='black', lw=0.8, linestyle='--')
    ax2.set_title("Rendimientos Diarios (%)", fontsize=10.5, fontweight='bold')
    ax2.set_ylabel("Retorno (%)")
    ax2.grid(True, linestyle=':', alpha=0.6)

    # 3. Volatilidad Móvil (10 días)
    ax3.plot(df_clean['date'], df_clean['rolling_volatility'] * 100, color='#D97706', lw=1.5, label="Volatilidad Móvil 10d (%)")
    ax3.scatter(anomalies['date'], anomalies['rolling_volatility'] * 100, color='#DC2626', s=45, zorder=5)
    ax3.set_title("Volatilidad Móvil (Ventana 10 días)", fontsize=10.5, fontweight='bold')
    ax3.set_ylabel("Volatilidad (%)")
    ax3.set_xlabel("Fecha de Negociación")
    ax3.grid(True, linestyle=':', alpha=0.6)

    plt.tight_layout()
    plt.subplots_adjust(top=0.91)
    plt.savefig("docs/images/fig4_deteccion_anomalias_mercado.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated fig4_deteccion_anomalias_mercado.png")

# -------------------------------------------------------------
# FIGURA 5: Trazabilidad y Latencia de Agentes
# -------------------------------------------------------------
def generate_fig5_latency():
    agents = [
        "Data Ingestion\nAgent",
        "Financial Analysis\nAgent",
        "News & Context\nAgent (RAG)",
        "Risk & Anomaly\nAgent (IF+Rules)",
        "Report Generator\nAgent (LLM)"
    ]
    # Real durations recorded from execution trace in SQLite (Run dc6829aa)
    durations = [2, 1, 817, 72, 4794]
    colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']

    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    bars = ax.bar(agents, durations, color=colors, edgecolor='#1E293B', lw=1, width=0.55)
    
    ax.set_yscale('log')
    ax.set_title("Tiempos de Ejecución y Latencia por Agente (Escala Logarítmica)\n[Evidencia Verificada en SQLite Run `dc6829aa`]", 
                 fontsize=12, fontweight='bold', color='#0F172A', pad=12)
    ax.set_ylabel("Duración de Ejecución (milisegundos, log)")
    ax.set_ylim(0.5, 10000)

    for bar, duration in zip(bars, durations):
        height = bar.get_height()
        label_text = f"{duration} ms" if duration < 1000 else f"{duration/1000:.2f} s\n({duration} ms)"
        ax.annotate(label_text,
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5), textcoords="offset points",
                    ha='center', va='bottom', fontsize=8.5, fontweight='bold')

    ax.text(0.98, 0.90, "Tiempo Total del Pipeline: 5.69 s\nDeterministas: <80 ms\nLLM + RAG: ~5.61 s", 
            transform=ax.transAxes, fontsize=9, ha='right', va='top',
            bbox=dict(boxstyle="round,pad=0.5", fc="#F8FAFC", ec="#CBD5E1", lw=1))

    plt.tight_layout()
    plt.savefig("docs/images/fig5_trazabilidad_latencia_agentes.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated fig5_trazabilidad_latencia_agentes.png")

# -------------------------------------------------------------
# FIGURA 6: Representación Visual del Dashboard Streamlit
# -------------------------------------------------------------
def generate_fig6_ui_mockup():
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=300)
    ax.axis('off')
    
    # Background frame
    frame = patches.FancyBboxPatch((0.02, 0.02), 0.96, 0.96,
                                  boxstyle="round,pad=0.01,rounding_size=0.015",
                                  facecolor="#F8FAFC", edgecolor="#94A3B8", lw=1.5)
    ax.add_patch(frame)

    # Sidebar
    sidebar = patches.Rectangle((0.02, 0.02), 0.25, 0.96, facecolor="#0F172A", edgecolor="none")
    ax.add_patch(sidebar)
    ax.text(0.04, 0.93, "CONFIGURACIÓN", color="#94A3B8", fontsize=10, fontweight='bold')
    ax.text(0.04, 0.87, "Seleccionar Ticker:", color="#E2E8F0", fontsize=8.5)
    
    # Input box ticker
    ax.add_patch(patches.Rectangle((0.04, 0.81), 0.21, 0.04, facecolor="#1E293B", edgecolor="#475569"))
    ax.text(0.05, 0.825, "DEMO_LEVR", color="#38BDF8", fontsize=9, fontweight='bold')
    
    ax.text(0.04, 0.75, "Período de Análisis:", color="#E2E8F0", fontsize=8.5)
    ax.add_patch(patches.Rectangle((0.04, 0.69), 0.21, 0.04, facecolor="#1E293B", edgecolor="#475569"))
    ax.text(0.05, 0.705, "1Y (1 Año)", color="#F1F5F9", fontsize=9)

    # Run button
    ax.add_patch(patches.FancyBboxPatch((0.04, 0.60), 0.21, 0.05, boxstyle="round,pad=0.005", facecolor="#EF4444", edgecolor="none"))
    ax.text(0.145, 0.625, "Ejecutar Analisis", color="white", fontsize=9.5, fontweight='bold', ha='center', va='center')

    # Main content area
    ax.text(0.30, 0.92, "Aplicación Multi-Agente de Análisis Financiero y Alertas de Riesgo", 
            color="#0F172A", fontsize=13, fontweight='bold')
    
    # Disclaimer banner
    ax.add_patch(patches.FancyBboxPatch((0.30, 0.84), 0.66, 0.05, boxstyle="round,pad=0.005", facecolor="#FEF3C7", edgecolor="#D97706"))
    ax.text(0.31, 0.86, "[!] Aviso Legal: Herramienta academica de apoyo analitico. No constituye asesoramiento financiero.", 
            color="#92400E", fontsize=8)

    # Execution status & metric
    ax.add_patch(patches.FancyBboxPatch((0.30, 0.71), 0.42, 0.10, boxstyle="round,pad=0.008", facecolor="#FFFFFF", edgecolor="#CBD5E1"))
    ax.text(0.32, 0.78, "ID de Ejecucion: `dc64b94e-ed9f-4a78-9028-e419a6b96f3c`", color="#64748B", fontsize=8)
    ax.text(0.32, 0.74, "Estado: COMPLETED (5 agentes exitosos en 5.69 s)", color="#15803D", fontsize=9, fontweight='bold')

    # Risk Score Card
    ax.add_patch(patches.FancyBboxPatch((0.74, 0.71), 0.22, 0.10, boxstyle="round,pad=0.008", facecolor="#FEF2F2", edgecolor="#DC2626", lw=1.5))
    ax.text(0.85, 0.78, "PUNTUACION DE RIESGO", color="#991B1B", fontsize=8, fontweight='bold', ha='center')
    ax.text(0.85, 0.73, "100.0 / 100", color="#DC2626", fontsize=15, fontweight='bold', ha='center')
    ax.text(0.85, 0.69, "NIVEL: CRITICO", color="#991B1B", fontsize=8.5, fontweight='bold', ha='center')

    # Report Body Columns
    # Col 1: Executive Summary & Findings
    ax.add_patch(patches.FancyBboxPatch((0.30, 0.38), 0.32, 0.30, boxstyle="round,pad=0.008", facecolor="#FFFFFF", edgecolor="#CBD5E1"))
    ax.text(0.315, 0.65, "Resumen Ejecutivo y Hallazgos", color="#0F172A", fontsize=9.5, fontweight='bold')
    summary_text = (
        "Leverage Inc (DEMO_LEVR) presenta un nivel de\n"
        "riesgo critico (100.0). Se constata deterioro\n"
        "sostenido en ingresos (-5.26%), elevado\n"
        "apalancamiento (Deuda/EBITDA = 4.64x)\n"
        "y estres severo de liquidez circulante."
    )
    ax.text(0.315, 0.54, summary_text, color="#334155", fontsize=8)
    ax.text(0.315, 0.44, "- Hallazgo: Caida acumulada >30%\n- Hallazgo: 9 dias anomalos de mercado", color="#0369A1", fontsize=7.8)

    # Col 2: Active Risk Alerts & Actions
    ax.add_patch(patches.FancyBboxPatch((0.64, 0.38), 0.32, 0.30, boxstyle="round,pad=0.008", facecolor="#FFFFFF", edgecolor="#CBD5E1"))
    ax.text(0.655, 0.65, "Alertas de Riesgo Activas (6)", color="#DC2626", fontsize=9.5, fontweight='bold')
    alerts_text = (
        "[ALTO] Deuda Neta/EBITDA: 4.64x (> 3.5x)\n"
        "[ALTO] Current Ratio: 0.87x (< 1.0x)\n"
        "[MEDIO] Caida Ingresos: -5.26% (< 0%)\n"
        "[MEDIO] Max Drawdown: 35.41% (> 30%)\n"
        "[MEDIO] Caida Efectivo: -11.11% (< -10%)\n"
        "[MEDIO] Anomalias Mercado: 9 dias (IF)"
    )
    ax.text(0.655, 0.48, alerts_text, color="#1E293B", fontsize=7.6, fontfamily='monospace')

    # Bottom Actions Box
    ax.add_patch(patches.FancyBboxPatch((0.30, 0.06), 0.66, 0.28, boxstyle="round,pad=0.008", facecolor="#FFFFFF", edgecolor="#CBD5E1"))
    ax.text(0.315, 0.31, "Acciones de Revision Recomendadas por el Sistema:", color="#0F172A", fontsize=9, fontweight='bold')
    ax.text(0.315, 0.24, "(*) 1. Auditar el calendario de vencimientos de deuda a corto plazo y covenants bancarios.", color="#15803D", fontsize=8)
    ax.text(0.315, 0.18, "(*) 2. Evaluar plan de contingencia de liquidez ante ratio circulante deficitario (0.87x).", color="#15803D", fontsize=8)
    ax.text(0.315, 0.12, "(*) 3. Investigar las causas operativas de la contraccion continuada del margen EBITDA.", color="#15803D", fontsize=8)

    plt.tight_layout()
    plt.savefig("docs/images/fig6_interfaz_usuario_dashboard.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated fig6_interfaz_usuario_dashboard.png")

if __name__ == "__main__":
    generate_fig1_architecture()
    generate_fig2_workflow()
    generate_fig3_financial_comparison()
    generate_fig4_anomaly_detection()
    generate_fig5_latency()
    generate_fig6_ui_mockup()
    print("All figures successfully generated in docs/images/")
