from typing import Dict, Any
from app.domain.models import AnalysisState, NewsItem
from app.analytics.rag_engine import create_news_vectorstore, get_relevant_news_context

def gather_news_context_agent(state: AnalysisState) -> Dict[str, Any]:
    print(f"--- Gathering News Context for {state.ticker} ---")
    
    if not state.news_data:
        # In this simplified MVP, the Data Ingestion agent loads news fixtures. 
        # But if it didn't, we would fetch it here.
        # Let's assume state.news_data was populated by data_ingestion.py if available.
        return {
            "warnings": state.warnings + [{"agent": "News & Context Agent", "message": "No news data available for context."}]
        }
        
    try:
        # In a real scenario with lots of documents, we would use RAG.
        # Here we build the vector store and extract the most relevant pieces.
        vectorstore = create_news_vectorstore(state.news_data)
        
        # Query for general financial health and risks
        query = "What are the recent financial results, risks, leverage, or significant corporate events?"
        context_str = get_relevant_news_context(vectorstore, query=query, k=5)
        
        # We don't have a specific field for summarized news context in AnalysisState,
        # but the Report Generator will use state.news_data directly if needed, or we could pass this context via another mechanism.
        # Actually, let's just return a status. The report generator will do its own extraction if needed,
        # or we could append this summarized context to a new field if we extended AnalysisState.
        
        return {
            # Just acknowledging success
        }
    except Exception as e:
        # e.g., OpenAI API key not set for embeddings
        return {
            "warnings": state.warnings + [{"agent": "News & Context Agent", "message": f"RAG processing failed: {str(e)}"}]
        }
