import streamlit as st
import requests
import json
import time

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Análisis Financiero y Alertas de Riesgo",
    page_icon="📊",
    layout="wide"
)

st.title("Aplicación Multi-Agente de Análisis Financiero y Alertas de Riesgo")

st.markdown("""
> **Aviso Legal:** Herramienta de apoyo educativo y analítico únicamente. Esta aplicación no constituye asesoramiento financiero ni una recomendación de inversión.
""")

st.sidebar.header("Configuración")

ticker_option = st.sidebar.selectbox("Seleccione el Ticker", ["DEMO_STBL", "DEMO_LEVR", "DEMO_VOLT", "Personalizado (Ticker Real)"])
if ticker_option == "Personalizado (Ticker Real)":
    ticker = st.sidebar.text_input("Ingrese el Símbolo del Ticker (ej. AAPL, TSLA)", "AAPL").upper()
else:
    ticker = ticker_option

period = st.sidebar.selectbox("Período de Análisis", ["1M", "3M", "6M", "1Y"], index=3)

if st.sidebar.button("Ejecutar Análisis"):
    with st.spinner("Inicializando flujo de trabajo..."):
        try:
            resp = requests.post(f"{API_URL}/analyses", json={"ticker": ticker, "period": period})
            if resp.status_code == 200:
                run_id = resp.json()["run_id"]
                st.session_state["current_run_id"] = run_id
                st.success(f"Análisis iniciado: {run_id}")
            else:
                st.error("Error al iniciar el análisis.")
        except Exception as e:
            st.error(f"Error de conexión con la API: {e}")

run_id = st.session_state.get("current_run_id")

if run_id:
    st.subheader(f"ID de Ejecución: {run_id}")
    
    # Poll for status
    status_placeholder = st.empty()
    progress_placeholder = st.empty()
    
    is_completed = False
    
    # Simple polling loop
    for _ in range(30):
        try:
            status_resp = requests.get(f"{API_URL}/analyses/{run_id}")
            if status_resp.status_code == 200:
                data = status_resp.json()
                status = data["status"]
                
                status_placeholder.info(f"Estado: {status.upper()}")
                
                events_resp = requests.get(f"{API_URL}/analyses/{run_id}/events")
                if events_resp.status_code == 200:
                    events = events_resp.json()
                    agents_completed = [e['agent_name'] for e in events if e['status'] == 'success']
                    progress_placeholder.text(f"Agentes completados: {', '.join(agents_completed)}")
                
                if status in ["completed", "error"]:
                    is_completed = True
                    if status == "completed":
                        status_placeholder.success("¡Análisis completado con éxito!")
                        st.metric("Puntuación de Riesgo Global", f"{data['risk_score']:.1f}/100", data['risk_level'].upper())
                    else:
                        status_placeholder.error("El análisis ha fallado.")
                    break
                    
        except Exception:
            pass
            
        time.sleep(2)
        
    if is_completed and data.get("status") == "completed":
        st.header("Informe Ejecutivo")
        
        try:
            report_resp = requests.get(f"{API_URL}/analyses/{run_id}/report")
            if report_resp.status_code == 200:
                report = report_resp.json()
                
                st.subheader("Resumen Ejecutivo")
                st.write(report.get("executive_summary", ""))
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Hallazgos Clave")
                    for k in report.get("key_findings", []):
                        st.markdown(f"- {k}")
                        
                    st.subheader("Señales Positivas")
                    for p in report.get("positive_signals", []):
                        st.markdown(f"- {p}")
                        
                with col2:
                    st.subheader("Alertas de Riesgo")
                    for r in report.get("risk_alerts", []):
                        st.markdown(f"- 🚨 {r}")
                        
                    st.subheader("Acciones de Revisión Recomendadas")
                    for a in report.get("recommended_review_actions", []):
                        st.markdown(f"- ✅ {a}")
                        
                st.subheader("Calidad de Datos y Fuentes")
                for d in report.get("data_quality_notes", []):
                    st.markdown(f"- {d}")
                for s in report.get("sources", []):
                    st.markdown(f"- 🔗 {s}")
                    
                st.download_button("Descargar Informe (JSON)", data=json.dumps(report, indent=2, ensure_ascii=False), file_name=f"{ticker}_reporte.json")
                
        except Exception as e:
            st.error(f"Error al obtener el informe: {e}")
