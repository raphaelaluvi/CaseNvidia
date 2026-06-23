"""
Script principal do Dia 1: dado o nome de uma startup, busca URLs
candidatas, coleta o conteúdo de cada uma e salva tudo em disco com
metadados de rastreabilidade (fonte, data de coleta, método).

Uso:
    python -m src.scraping.search_and_fetch "nome da startup"

Saída:
    data/raw/<nome_startup_slug>/<timestamp>.json
    Um arquivo JSON por URL coletada, dentro de uma pasta por startup.

Este é o ponto de entrada do Entregável 1 (Pipeline de scraping) em
sua versão mínima. Nos próximos dias isso se torna o "Scraper Agent"
dentro do grafo LangGraph.
"""
import json
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone

from src.scraping.search import buscar_urls_candidatas
from src.scraping.fetcher import fetch_page

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

DATA_RAW_DIR = Path("data/raw")


def _slug(texto: str) -> str:
    return (
        texto.strip()
        .lower()
        .replace(" ", "_")
        .replace("/", "-")
    )


def coletar_startup(
    nome_startup: str, max_urls: int = 5, urls_diretas: list[str] | None = None
) -> list[dict]:
    """
    Pipeline completo do Dia 1 para uma startup:
    1. busca URLs candidatas (ou usa `urls_diretas`, se fornecidas)
    2. coleta o conteúdo de cada uma
    3. salva cada documento em disco com metadados de rastreabilidade

    O parâmetro `urls_diretas` existe como alternativa de contingência:
    buscadores como o DuckDuckGo podem bloquear requisições automatizadas
    (rate-limit / anti-bot) dependendo da rede. Se isso acontecer, você
    pode passar manualmente as URLs que quer coletar (ex: site oficial
    da startup, página no Distrito, etc.) e o resto do pipeline funciona
    normalmente.

    Retorna a lista de documentos coletados (como dicts), também
    salvos em disco para uso pelo Extractor (Dia 2).
    """
    if urls_diretas:
        logger.info("Usando %d URLs diretas fornecidas manualmente.", len(urls_diretas))
        urls = urls_diretas
    else:
        logger.info("Buscando URLs candidatas para: %s", nome_startup)
        urls = buscar_urls_candidatas(nome_startup, max_resultados=max_urls)

    if not urls:
        logger.warning(
            "Nenhuma URL encontrada para '%s'. Nada será coletado.", nome_startup
        )
        return []

    logger.info("Encontradas %d URLs. Iniciando coleta...", len(urls))

    pasta_startup = DATA_RAW_DIR / _slug(nome_startup)
    pasta_startup.mkdir(parents=True, exist_ok=True)

    documentos_coletados = []

    for i, url in enumerate(urls, start=1):
        logger.info("[%d/%d] Coletando: %s", i, len(urls), url)
        documento = fetch_page(url, fonte_tipo="busca_geral")

        if documento.erro:
            logger.warning("  -> Falhou: %s", documento.erro)
        else:
            logger.info(
                "  -> OK (%d caracteres de texto)", len(documento.texto)
            )

        documentos_coletados.append(documento.to_dict())

        # Salva cada documento individualmente, com timestamp único,
        # para rastreabilidade completa (um arquivo = uma fonte coletada).
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
        caminho_arquivo = pasta_startup / f"{timestamp}_{i}.json"
        caminho_arquivo.write_text(
            json.dumps(documento.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    logger.info(
        "Coleta finalizada para '%s'. %d documentos salvos em %s",
        nome_startup,
        len(documentos_coletados),
        pasta_startup,
    )
    return documentos_coletados


def main():
    if len(sys.argv) < 2:
        print('Uso: python -m src.scraping.search_and_fetch "nome da startup"')
        print(
            'Ou, se a busca automática falhar na sua rede:\n'
            '  python -m src.scraping.search_and_fetch "nome da startup" '
            '--urls https://site1.com,https://site2.com'
        )
        sys.exit(1)

    if "--urls" in sys.argv:
        idx = sys.argv.index("--urls")
        nome_startup = " ".join(sys.argv[1:idx])
        urls_diretas = sys.argv[idx + 1].split(",")
        coletar_startup(nome_startup, urls_diretas=urls_diretas)
    else:
        nome_startup = " ".join(sys.argv[1:])
        coletar_startup(nome_startup)


if __name__ == "__main__":
    main()
