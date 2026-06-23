"""
Campanha de coleta de notícias com mineração de relevância (modo misto).

Diferente do search_and_fetch.py (que busca por nome de startup),
este script percorre as FONTES de notícia configuradas em
src.scraping.fontes, coleta título+resumo de cada item (fase 1, barata),
aplica o filtro de relevância de IA, e só aprofunda (fase 2, busca o
texto completo) os itens que parecem relevantes ao escopo do projeto.

Uso:
    python -m src.scraping.coletar_noticias

Saída:
    data/raw/_noticias/<fonte_slug>/<timestamp>.json
    Um arquivo por notícia, com indicação clara de quais foram
    aprofundadas (texto_completo preenchido) e quais não.

IMPORTANTE: os parsers de listagem (src.scraping.noticias) usam
seletores CSS que são uma primeira tentativa razoável, mas podem
precisar de ajuste fino dependendo da estrutura real de cada site.
Se uma fonte retornar 0 itens, rode primeiro:
    python -m src.scraping.inspecionar_fontes
para inspecionar a estrutura HTML real e ajustar os seletores.
"""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from src.scraping.noticias import (
    coletar_listagem_brazil_journal,
    coletar_listagem_neofeed,
    aprofundar_itens_relevantes,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

DATA_RAW_NOTICIAS_DIR = Path("data/raw/_noticias")

# Cada fonte de notícia é um par (slug, nome_exibicao, função_coletora).
# Para adicionar uma nova fonte: criar a função coletar_listagem_<fonte>
# em src.scraping.noticias e registrar aqui.
FONTES_NOTICIA = [
    ("brazil_journal", "Brazil Journal", coletar_listagem_brazil_journal),
    ("neofeed", "NeoFeed", coletar_listagem_neofeed),
]


def _slug(texto: str) -> str:
    return texto.strip().lower().replace(" ", "_").replace("/", "-")


def executar_campanha(max_itens_por_fonte: int = 15):
    """
    Executa a campanha completa: para cada fonte de notícia configurada
    em FONTES_NOTICIA, coleta a listagem, filtra por relevância e
    aprofunda os itens que interessam. Salva tudo em disco com
    rastreabilidade.
    """
    resultado_geral = {}

    for slug_fonte, nome_fonte, funcao_coletora in FONTES_NOTICIA:
        logger.info("=== Coletando listagem: %s ===", nome_fonte)
        itens = funcao_coletora(max_itens=max_itens_por_fonte)
        logger.info("Itens encontrados na listagem: %d", len(itens))

        if not itens:
            logger.warning(
                "Nenhum item coletado de %s. Possíveis causas: "
                "(1) bloqueio de rede/anti-bot, (2) estrutura HTML diferente "
                "do esperado pelos seletores atuais. Rode "
                "`python -m src.scraping.inspecionar_fontes` para diagnosticar.",
                nome_fonte,
            )
            resultado_geral[slug_fonte] = {"total_itens": 0, "itens_aprofundados": 0}
            continue

        relevantes_antes = [i for i in itens if i.relevancia.get("vale_aprofundar")]
        logger.info(
            "Itens com sinal de IA (serão aprofundados): %d de %d",
            len(relevantes_antes),
            len(itens),
        )

        itens = aprofundar_itens_relevantes(itens)

        # Salva tudo em disco, com rastreabilidade.
        pasta_fonte = DATA_RAW_NOTICIAS_DIR / slug_fonte
        pasta_fonte.mkdir(parents=True, exist_ok=True)

        for i, item in enumerate(itens, start=1):
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
            caminho_arquivo = pasta_fonte / f"{timestamp}_{i}.json"
            caminho_arquivo.write_text(
                json.dumps(item.to_dict(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        resultado_geral[slug_fonte] = {
            "total_itens": len(itens),
            "itens_aprofundados": sum(1 for i in itens if i.texto_completo),
        }

    logger.info("=== Resumo da campanha ===")
    for fonte, stats in resultado_geral.items():
        logger.info(
            "  %s: %d itens coletados, %d aprofundados (texto completo)",
            fonte,
            stats["total_itens"],
            stats["itens_aprofundados"],
        )

    return resultado_geral


if __name__ == "__main__":
    executar_campanha()
