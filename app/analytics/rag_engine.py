import os
from typing import List, Dict, Any
from app.domain.models import NewsItem
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

def create_news_vectorstore(news_items: List[NewsItem]) -> FAISS:
    docs = []
    for n in news_items:
        # Create a document for each news item
        content = f"Headline: {n.headline}\nSummary: {n.summary}\nDate: {n.date}\nSource: {n.source}\nEvent Type: {n.event_type}"
        docs.append(Document(page_content=content, metadata={"date": str(n.date), "source": n.source, "headline": n.headline}))
        
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(docs, embeddings)
    return vectorstore

def get_relevant_news_context(vectorstore: FAISS, query: str = "Company risk and financial performance", k: int = 5) -> str:
    docs = vectorstore.similarity_search(query, k=k)
    if not docs:
        return "No relevant news context found."
        
    context_parts = []
    for i, doc in enumerate(docs):
        context_parts.append(f"--- Document {i+1} ---\n{doc.page_content}")
        
    return "\n\n".join(context_parts)
