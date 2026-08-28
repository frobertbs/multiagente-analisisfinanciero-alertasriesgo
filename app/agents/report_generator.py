import json
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.domain.models import AnalysisState, ExecutiveReport

def generate_report_agent(state: AnalysisState) -> Dict[str, Any]:
    print(f"--- Generating Report for {state.ticker} ---")
    
    if not state.financial_analysis or not state.risk_analysis:
        return {
            "errors": state.errors + [{"agent": "Report Generator Agent", "message": "Missing necessary analysis results for report generation."}]
        }
        
    try:
        # We need OPENAI_API_KEY set in environment
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        # Build Context string
        company_name = state.company_name or state.ticker
        
        signals_formatted = []
        for s in state.risk_analysis.signals:
            obs = f"{s.observed_value:.2f}"
            thr = f"{s.threshold}" if s.threshold is not None else "N/A"
            signals_formatted.append(f"[{s.severity.upper()}] {s.category}: {obs} (Umbral: {thr}) - {s.description}")
            
        risk_signals_str = "\n".join(signals_formatted)
        
        news_str = "\n".join([f"- {n.date}: {n.headline} ({n.source})" for n in state.news_data])
        
        context = f"""
        Company: {company_name} ({state.ticker})
        Analysis Period: {state.analysis_period}
        
        Risk Score: {state.risk_analysis.score}/100 ({state.risk_analysis.level})
        Risk Explanation: {state.risk_analysis.explanation}
        
        Active Risk Signals:
        {risk_signals_str}
        
        Recent News Context:
        {news_str}
        """
        
        system_prompt = """
        You are a senior financial analyst and risk manager. 
        Write an executive report based ONLY on the provided context.
        Do not invent figures, news, ratios, or sources.
        
        IMPORTANT: Write the entire content of the report in Spanish (Español).
        
        CRITICAL INSTRUCTION FOR `risk_alerts`:
        In the `risk_alerts` JSON array, you MUST list the exact strings provided in the "Active Risk Signals" section of the context (including the severity, calculated metric value, and threshold). Do not summarize them. Just copy them exactly as they appear.
        
        Output MUST be valid JSON conforming to the following structure:
        {{
          "executive_summary": "...",
          "risk_level": "...",
          "risk_score": 0.0,
          "key_findings": ["..."],
          "risk_alerts": ["..."],
          "positive_signals": ["..."],
          "recommended_review_actions": ["..."],
          "data_quality_notes": ["..."],
          "sources": ["..."],
          "disclaimer": "Herramienta de apoyo educativo y analítico únicamente. Esta aplicación no constituye asesoramiento financiero ni una recomendación de inversión."
        }}
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "Context:\n{context}\n\nGenerate the JSON report:")
        ])
        
        chain = prompt | llm
        
        response = chain.invoke({"context": context})
        
        # Parse JSON from response. (langchain parser can be used, but keeping it simple)
        response_text = response.content.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:-3]
        elif response_text.startswith("```"):
            response_text = response_text[3:-3]
            
        report_data = json.loads(response_text)
        report = ExecutiveReport(**report_data)
        
        return {
            "report": report
        }
        
    except Exception as e:
        return {
            "errors": state.errors + [{"agent": "Report Generator Agent", "message": f"LLM generation failed: {str(e)}"}]
        }
