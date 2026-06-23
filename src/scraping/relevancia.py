"""
Filtro de relevância AI-native (mineração leve, sem custo de LLM).

Antes de gastar uma chamada de LLM (Classifier Agent, Dia 3) ou uma
requisição extra de scraping, fazemos uma triagem rápida e barata por
palavras-chave para decidir se um texto (notícia, descrição de startup)
tem sinal suficiente de uso de IA para valer a pena aprofundar a coleta.

Isso implementa a ideia de "minerar para selecionar apenas o que é
interessante", reduzindo ruído antes das etapas mais caras do pipeline
(scraping profundo, extração estruturada via LLM, classificação).
"""
import re

# Termos que indicam uso de IA/ML, organizados por força de sinal.
# Termos fortes = quase certeza de relevância (LLM, agentes, IA generativa).
# Termos médios = indicam tecnologia mas podem ser genéricos demais sozinhos.
TERMOS_FORTES = [
    "inteligência artificial",
    "ia generativa",
    "llm",
    "large language model",
    "modelo de linguagem",
    "machine learning",
    "aprendizado de máquina",
    "agentes de ia",
    "agente de ia",
    "deep learning",
    "redes neurais",
    "chatgpt",
    "openai",
    "anthropic",
    "nvidia",
    "gpu",
    "rag",
    "retrieval augmented",
    "computer vision",
    "visão computacional",
    "nlp",
    "processamento de linguagem natural",
]

TERMOS_MEDIOS = [
    "automação",
    "algoritmo",
    "dados em tempo real",
    "personalização",
    "predição",
    "preditivo",
    "copilot",
    "assistente virtual",
    "chatbot",
]


def calcular_score_relevancia_ia(texto: str) -> dict:
    """
    Calcula um score simples de relevância AI a partir de contagem de
    termos-chave. Não substitui o Classifier Agent (que usará LLM no
    Dia 3) — é uma triagem barata para decidir o que vale aprofundar.

    Retorna um dict com o score, os termos encontrados e uma sugestão
    booleana de "vale aprofundar a coleta".
    """
    texto_lower = texto.lower()

    termos_fortes_encontrados = [
        termo for termo in TERMOS_FORTES if termo in texto_lower
    ]
    termos_medios_encontrados = [
        termo for termo in TERMOS_MEDIOS if termo in texto_lower
    ]

    # Pesos: termo forte vale 3 pontos, termo médio vale 1 ponto.
    score = len(termos_fortes_encontrados) * 3 + len(termos_medios_encontrados) * 1

    # Heurística de corte: qualquer termo forte, ou 2+ termos médios,
    # já justifica aprofundar a coleta.
    vale_aprofundar = len(termos_fortes_encontrados) >= 1 or len(termos_medios_encontrados) >= 2

    return {
        "score": score,
        "termos_fortes_encontrados": termos_fortes_encontrados,
        "termos_medios_encontrados": termos_medios_encontrados,
        "vale_aprofundar": vale_aprofundar,
    }


def extrair_trecho_relevante(texto: str, janela_chars: int = 200) -> str:
    """
    Extrai um pequeno trecho do texto em torno do primeiro termo forte
    encontrado, útil para preview rápido sem precisar ler o texto todo.
    """
    texto_lower = texto.lower()
    for termo in TERMOS_FORTES:
        idx = texto_lower.find(termo)
        if idx != -1:
            inicio = max(0, idx - janela_chars // 2)
            fim = min(len(texto), idx + len(termo) + janela_chars // 2)
            return texto[inicio:fim].strip()
    return texto[:janela_chars].strip()
