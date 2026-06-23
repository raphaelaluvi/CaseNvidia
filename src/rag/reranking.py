import os
from typing import List, Dict
from .config import OPENROUTER_API_KEY, OPENROUTER_BASE

import httpx

def rerank_with_openrouter(query: str, passages: List[Dict], top_k: int = 5) -> List[Dict]:
    """
    Reordena (rerank) trechos recuperados usando um LLM via OpenRouter.
    Se a chave de API não estiver definida, aplica um ranking heurístico simples.
    Retorna os trechos com campo 'score' (0.0-1.0).
    """
    if not OPENROUTER_API_KEY:
        # fallback simples: score decrescente heurístico
        for i, p in enumerate(passages[:top_k]):
            p["score"] = 1.0 - (i * 0.01)
        return passages[:top_k]

    url = f"{OPENROUTER_BASE}/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}

    scored = []
    # Para cada trecho (até 50) pedimos um número de 0-100 indicando relevância
    for p in passages[:min(len(passages), 50)]:
        prompt = (
            f"Avalie a relevância do seguinte trecho para a consulta:\nConsulta: {query}\nTrecho: {p.get('document') or p.get('text')[:500]}\n"
            "Responda apenas com um número entre 0 e 100 representando a relevância."
        )
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 16,
            "temperature": 0.0,
        }
        try:
            r = httpx.post(url, json=payload, headers=headers, timeout=20.0)
            r.raise_for_status()
            data = r.json()
            text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            num = 0.0
            for tok in text.split():
                try:
                    num = float(tok)
                    break
                except Exception:
                    continue
            p["score"] = num / 100.0
        except Exception:
            p["score"] = 0.0
        scored.append(p)

    scored.sort(key=lambda x: x.get("score", 0.0), reverse=True)
    return scored[:top_k]