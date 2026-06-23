# NVIDIA Startup AI Radar

Plataforma multi-agente para mapear startups brasileiras AI-native, diagnosticar maturidade técnica e recomendar tecnologias NVIDIA, gerando briefing executivo para o time de Startups & VCs da NVIDIA Brasil.

> Projeto baseado no TAPI: [NVIDIA Startup AI Radar](https://inteliacademyclub.github.io/autoestudos/projetos/nvidia/nvidia-startup-ai-radar)

## Stack

- **Orquestração de agentes**: LangGraph
- **LLM**: Groq (Llama 3.3 / outros modelos disponíveis na Groq)
- **Embeddings**: sentence-transformers (local, sem custo de API)
- **Banco vetorial**: Qdrant (Docker local)
- **Banco estruturado**: PostgreSQL (Docker local)
- **Reranking**: Cohere Rerank (free tier)
- **Scraping**: requests + BeautifulSoup (Dia 1) → evolui para Playwright/trafilatura se necessário
- **Interface**: a definir (Dia 6)

## Roadmap de 7 dias

| Dia | Bloco | Entregável TAPI |
|---|---|---|
| 1 | Setup + scraper mínimo | Entregável 1 |
| 2 | Extractor + banco estruturado | Entregável 1 |
| 3 | Esqueleto LangGraph (pipeline ponta a ponta) | Entregável 2 |
| 4 | RAG NVIDIA com reranking | Entregável 3 |
| 5 | Motor de recomendação + Briefing Agent | Entregável 4 |
| 6 | Interface web | Entregável 5 |
| 7 | Diferencial + polimento | Entregável 6 |

## Setup rápido

```bash
# 1. Criar e ativar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Copiar variáveis de ambiente e preencher
cp .env.example .env
# editar .env com sua GROQ_API_KEY

# 4. Subir Qdrant + Postgres
docker compose up -d

# 5. Testar o scraper do Dia 1
python -m src.scraping.search_and_fetch "nome da startup"
```

## Estrutura do projeto

```text
src/
  agents/         # Agentes LangGraph (Planner, Scraper, Extractor, Classifier, Validator, RAG, Recommendation, Briefing)
  scraping/        # Coleta de dados públicos
  extraction/      # Estruturação de texto não estruturado -> JSON
  storage/         # Acesso a Postgres e Qdrant
  rag/             # Pipeline RAG (chunking, embeddings, busca híbrida, reranking)
  recommendation/  # Motor de recomendação NVIDIA
  api/             # Backend para a interface web (Dia 6)
data/
  raw/             # Dados brutos coletados (HTML, texto extraído, com metadados de fonte)
  processed/       # Dados estruturados
docs/              # Documentação e decisões de arquitetura
tests/             # Testes
```

## Status atual

- [x] Dia 1 — Setup + scraper mínimo
- [ ] Dia 2 — Extractor + banco estruturado
- [ ] Dia 3 — Pipeline LangGraph ponta a ponta
- [ ] Dia 4 — RAG com reranking
- [ ] Dia 5 — Motor de recomendação + briefing
- [ ] Dia 6 — Interface web
- [ ] Dia 7 — Diferencial + polimento
