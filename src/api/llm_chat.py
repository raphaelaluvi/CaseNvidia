from __future__ import annotations

import json

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from src.extraction.config import GROQ_API_KEY
from src.rag.api import answer_query


def _serialize_context(startup_payload: dict | None) -> str:
    if not startup_payload:
        return "Nenhuma startup previamente analisada foi selecionada."
    data = {
        "startup": startup_payload.get("name"),
        "segment": startup_payload.get("segment"),
        "city": startup_payload.get("city"),
        "aiScore": startup_payload.get("aiScore"),
        "classification": startup_payload.get("classification"),
        "validationStatus": startup_payload.get("validationStatus"),
        "summary": startup_payload.get("summary"),
        "signals": startup_payload.get("signals"),
        "recommendations": startup_payload.get("recommendations"),
        "briefing": startup_payload.get("executiveBrief"),
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def answer_chat_message(message: str, startup_payload: dict | None = None) -> dict:
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY não configurada para o chat.")

    rag_query = message
    if startup_payload and startup_payload.get("name"):
        rag_query = f"{startup_payload['name']} NVIDIA products fit {message}"
    rag_context = answer_query(rag_query)

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        max_tokens=900,
        api_key=GROQ_API_KEY,
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "Você é um analista sênior do NVIDIA Startup AI Radar. "
                    "Responda em português do Brasil, com tom executivo e objetivo. "
                    "Use o contexto da startup e o contexto RAG NVIDIA como base. "
                    "Se houver incerteza, explicite a limitação em vez de inventar."
                ),
            ),
            (
                "user",
                (
                    "Startup selecionada:\n{startup_context}\n\n"
                    "Contexto RAG NVIDIA:\n{rag_context}\n\n"
                    "Pergunta do usuário:\n{message}"
                ),
            ),
        ]
    )
    response = llm.invoke(
        prompt.format_messages(
            startup_context=_serialize_context(startup_payload),
            rag_context=json.dumps(rag_context.model_dump(), ensure_ascii=False, indent=2),
            message=message,
        )
    )
    return {
        "answer": response.content,
        "sources": [
            {
                "citation": item.citation,
                "title": item.source_title,
                "url": item.source_url,
            }
            for item in rag_context.items[:5]
        ],
    }
