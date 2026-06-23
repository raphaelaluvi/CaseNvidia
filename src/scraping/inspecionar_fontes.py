"""
Script de inspeção (uso único, não faz parte do pipeline final).

Objetivo: baixar o HTML de páginas-chave (Cubo, Brazil Journal) e
mostrar pistas da estrutura (classes CSS, tags repetidas, possíveis
padrões de "card" de startup ou notícia) para que possamos escrever
os parsers definitivos com precisão, em vez de adivinhar seletores.

Uso:
    python -m src.scraping.inspecionar_fontes
    python -m src.scraping.inspecionar_fontes --url https://outra-fonte.com

Saída:
    - Salva o HTML bruto em data/raw/_inspecao/<slug>.html
    - Imprime no terminal um resumo de classes CSS mais frequentes
      e trechos de possíveis "cards"
"""
import re
import sys
from collections import Counter
from pathlib import Path

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

SAIDA_DIR = Path("data/raw/_inspecao")

URLS_PADRAO = {
    "cubo_startups_portfolio": "https://cubo.itau/startups-portfolio",
    "brazil_journal_startups": "https://braziljournal.com/tag/startups/",
}


def inspecionar(nome: str, url: str):
    SAIDA_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\n{'=' * 70}")
    print(f"Inspecionando: {nome}")
    print(f"URL: {url}")
    print("=" * 70)

    try:
        resposta = requests.get(url, headers=HEADERS, timeout=15)
    except requests.RequestException as exc:
        print(f"ERRO ao buscar a URL: {exc}")
        return

    print(f"Status HTTP: {resposta.status_code}")
    print(f"Tamanho do HTML: {len(resposta.text)} caracteres")

    if resposta.status_code != 200:
        print("Status não-200, abortando inspeção desta URL.")
        return

    caminho_html = SAIDA_DIR / f"{nome}.html"
    caminho_html.write_text(resposta.text, encoding="utf-8")
    print(f"HTML salvo em: {caminho_html}\n")

    soup = BeautifulSoup(resposta.text, "lxml")

    # 1. Classes CSS mais frequentes (cards costumam repetir a mesma classe)
    todas_classes = []
    for tag in soup.find_all(class_=True):
        todas_classes.extend(tag.get("class"))

    contagem = Counter(todas_classes)
    print("=== Top 20 classes CSS mais frequentes ===")
    for classe, qtd in contagem.most_common(20):
        print(f"  {qtd:4d}x  .{classe}")

    # 2. Possíveis containers de card/artigo
    print("\n=== Possíveis containers de card/artigo (heurística) ===")
    palavras_chave = ["card", "item", "startup", "portfolio", "grid", "list", "post", "article", "noticia"]
    candidatos = set()
    for tag in soup.find_all(class_=True):
        classes = " ".join(tag.get("class"))
        if any(p in classes.lower() for p in palavras_chave):
            candidatos.add((tag.name, classes))

    for tag_name, classes in sorted(candidatos)[:30]:
        print(f"  <{tag_name} class=\"{classes}\">")

    # 3. Quantidade de tags <article> (comum em sites de notícia)
    articles = soup.find_all("article")
    print(f"\n=== Tags <article> encontradas: {len(articles)} ===")
    if articles:
        primeiro = articles[0]
        print("Trecho do primeiro <article> encontrado:")
        print(" ", primeiro.get_text(separator=" | ", strip=True)[:300])

    # 4. Scripts com JSON embutido (indício de app React/Vue carregando via JS)
    scripts_json = soup.find_all("script", type="application/json")
    print(f"\n=== Scripts application/json: {len(scripts_json)} ===")

    # 5. Conclusão rápida
    texto_total = len(soup.get_text(strip=True))
    print(f"\n=== Conclusão rápida (texto total extraído: {texto_total} chars) ===")
    if texto_total < 500:
        print(
            "  ATENÇÃO: pouco texto. Possível indício de conteúdo renderizado "
            "via JavaScript (pode precisar de Playwright)."
        )
    else:
        print("  HTML parece conter texto substancial no servidor (requests+BS4 deve bastar).")


def main():
    if "--url" in sys.argv:
        idx = sys.argv.index("--url")
        url = sys.argv[idx + 1]
        nome = url.replace("https://", "").replace("/", "_").strip("_")
        inspecionar(nome, url)
    else:
        for nome, url in URLS_PADRAO.items():
            inspecionar(nome, url)


if __name__ == "__main__":
    main()
