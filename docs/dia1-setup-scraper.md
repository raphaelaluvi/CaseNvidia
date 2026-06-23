# Dia 1 — Setup + Scraper mínimo

## Objetivo do dia
Ter o ambiente rodando localmente (Docker, Python, dependências) e um
scraper simples funcionando: dado o nome de uma startup, buscar URLs
relacionadas e coletar o texto principal de cada página, salvando em
disco com metadados de rastreabilidade (URL, data de coleta, status).

Isso é a base do **Entregável 1 (Pipeline de scraping)** do TAPI.

## Passo a passo

### 1. Criar contas / pegar chaves de API

- **Groq** (você já tem) → confirme que sua key está em `console.groq.com/keys`
- **Cohere** (vamos precisar só a partir do Dia 4, mas vale criar agora):
  1. Acesse https://dashboard.cohere.com/
  2. Crie uma conta gratuita
  3. Vá em "API Keys" e copie a "Trial key" (free tier, suficiente para desenvolvimento)

### 2. Instalar Docker (se ainda não tiver)

- Windows/Mac: instale o [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Linux: `sudo apt install docker.io docker-compose-plugin`

### 3. Clonar/posicionar o projeto e configurar o ambiente

```bash
cd nvidia-startup-ai-radar

python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# abra o .env e cole sua GROQ_API_KEY (e COHERE_API_KEY, se já tiver)
```

### 4. Subir os bancos locais

```bash
docker compose up -d
```

Verifique se subiu certo:

```bash
docker ps
# deve mostrar radar_qdrant e radar_postgres rodando

curl http://localhost:6333/collections
# deve retornar um JSON vazio (ainda sem collections) — confirma que o Qdrant está de pé
```

### 5. Testar o scraper

```bash
python -m src.scraping.search_and_fetch "Nubank"
```

Isso deve:
1. Buscar URLs relacionadas a "Nubank" via DuckDuckGo
2. Coletar o texto de cada página encontrada
3. Salvar em `data/raw/nubank/<timestamp>_N.json`

## ⚠️ Troubleshooting conhecido

Ao testar este pipeline, identifiquei um problema real que você pode
encontrar também: **o DuckDuckGo pode bloquear a busca automática**
com erro 403 (rate-limit ou proteção anti-bot — isso varia de rede
para rede e pode ser intermitente).

**Se isso acontecer**, use o modo de URLs diretas como alternativa,
passando manualmente as páginas que quer coletar:

```bash
python -m src.scraping.search_and_fetch "Nubank" --urls https://nubank.com.br,https://distrito.me/empresas/nubank
```

O restante do pipeline (fetch + limpeza + salvamento com rastreabilidade)
funciona independentemente da busca — isso eu testei e confirmei que
funciona corretamente.

**Solução definitiva a considerar no Dia 2/3**: trocar a busca por
uma API de busca paga/com chave (ex: Serper, Tavily, Brave Search API),
que é mais estável que fazer scraping direto da página HTML do
DuckDuckGo. Por ora, isso não bloqueia o progresso porque o fallback
manual funciona.

## Checklist de saída do Dia 1

- [ ] `docker compose up -d` sobe Qdrant e Postgres sem erro
- [ ] `.env` preenchido com `GROQ_API_KEY`
- [ ] `python -m src.scraping.search_and_fetch "<startup qualquer>"` roda sem travar
- [ ] Pelo menos 1 arquivo JSON aparece em `data/raw/<slug>/`
- [ ] O JSON contém: url, texto, fonte_tipo, coletado_em, status_http
- [ ] Primeiro commit no repositório Git (contribuição constante exigida pelo TAPI)

## O que vem no Dia 2

- Transformar o texto bruto salvo em `data/raw/` em dados estruturados
  (nome da empresa, setor, founders, tecnologias mencionadas) usando
  o LLM da Groq.
- Criar as tabelas no Postgres e persistir os dados estruturados.
- Esse será o **Extractor Agent** em sua primeira versão.
