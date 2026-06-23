# src/rag/api.py
from typing import List
from .embeddings import EmbeddingClient
from .store import init_chroma
from .retriever import retrieve
from .reranker import rerank_with_openrouter
from .config import RERANK_TOPK

def answer_query(query: str, collection: str = "nvidia_kb") -> str:
    """
    Fluxo simples de resposta:
    - gera embedding da query
    - recupera top-K do Chroma
    - rerankeia usando OpenRouter
    - concatena os trechos top para formar contexto (retorna contexto por enquanto)
    """
    emb = EmbeddingClient()
    q_emb = emb.embed([query])[0]
    client = init_chroma()
    res = retrieve(client, collection, q_emb)
    passages = []
    docs = res.get("documents", [[]])[0]
    metadatas = res.get("metadatas", [[]])[0]
    ids = res.get("ids", [[]])[0]
    for d, m, _id in zip(docs, metadatas, ids):
        passages.append({"id": _id, "text": d, "meta": m})

    scored = rerank_with_openrouter(query, passages, top_k=RERANK_TOPK)

    context = "\n\n".join([p["text"] for p in scored])
    return f"Contexto dos trechos mais relevantes:\n\n{context}\n\n(Use um LLM para gerar a resposta final com citações.)"