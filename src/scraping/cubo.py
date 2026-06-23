"""
Parser do diretório de startups do Cubo Itaú.

Diferente do módulo de notícias (que extrai título+resumo de artigos),
aqui o objetivo é extrair a LISTA DE EMPRESAS do portfólio do Cubo —
essa lista alimenta a "população" de startups que o resto do pipeline
(Search Planner, Scraper, Classifier) vai investigar uma a uma.

IMPORTANTE — leia antes de usar:
A estrutura HTML real de cubo.itau/startups-portfolio ainda não foi
inspecionada (a sandbox de desenvolvimento bloqueia esse domínio).
O parser abaixo foi escrito com seletores genéricos e heurísticos,
seguindo o mesmo princípio do parser de notícias. Antes de confiar
nos resultados, rode:

    python -m src.scraping.inspecionar_fontes

e compare a lista de "possíveis containers de card" impressa no
terminal com os seletores usados em `extrair_startups_do_html()`
abaixo. Ajuste os seletores conforme a estrutura real encontrada.
"""
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from src.scraping.fetcher import HEADERS

logger = logging.getLogger(__name__)

URL_VITRINE_CUBO = "https://cubo.itau/startups-portfolio"

DATA_RAW_DIR = Path("data/raw/_cubo")

# Palavras-chave usadas para tentar identificar o container de cada
# "card" de startup na página, e dentro dele, o nome/segmento/link.
# Ajustar conforme o resultado real do script de inspeção.
CLASSES_CANDIDATAS_CARD = ["card", "startup", "portfolio-item", "grid-item"]


@dataclass
class StartupCubo:
    nome: str
    segmento: str | None
    descricao_curta: str | None
    url_perfil: str | None
    fonte: str = "Cubo Itaú - Vitrine de Startups"
    coletado_em: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "nome": self.nome,
            "segmento": self.segmento,
            "descricao_curta": self.descricao_curta,
            "url_perfil": self.url_perfil,
            "fonte": self.fonte,
            "coletado_em": self.coletado_em,
        }


def _texto_de(tag) -> str | None:
    if tag is None:
        return None
    texto = tag.get_text(strip=True)
    return texto or None


def _normalizar_url(url: str | None, url_base: str) -> str | None:
    if not url:
        return None
    if url.startswith("/"):
        base = re.match(r"https?://[^/]+", url_base)
        if base:
            return base.group(0) + url
    return url


def extrair_startups_do_html(html: str, url_base: str = URL_VITRINE_CUBO) -> list[StartupCubo]:
    """
    Extrai a lista de startups a partir do HTML da vitrine do Cubo.

    Estratégia (heurística, a confirmar com inspeção real):
    1. Procura por elementos cuja classe contenha alguma das
       CLASSES_CANDIDATAS_CARD.
    2. Dentro de cada um, tenta achar nome (heading ou link),
       segmento (texto curto perto do nome) e link de perfil.

    Se essa heurística não encontrar nada, retorna lista vazia e
    registra um warning — o chamador deve então usar o script de
    inspeção para descobrir os seletores corretos.
    """
    soup = BeautifulSoup(html, "lxml")
    startups: list[StartupCubo] = []

    candidatos = []
    for tag in soup.find_all(class_=True):
        classes = " ".join(tag.get("class")).lower()
        if any(palavra in classes for palavra in CLASSES_CANDIDATAS_CARD):
            candidatos.append(tag)

    if not candidatos:
        logger.warning(
            "Nenhum card de startup identificado pela heurística de classes "
            "%s. Rode `python -m src.scraping.inspecionar_fontes` para "
            "descobrir a estrutura real e ajustar CLASSES_CANDIDATAS_CARD "
            "em src/scraping/cubo.py.",
            CLASSES_CANDIDATAS_CARD,
        )
        return startups

    vistos = set()
    for card in candidatos:
        nome_tag = card.find(["h1", "h2", "h3", "h4", "strong"])
        nome = _texto_de(nome_tag)

        if not nome or nome in vistos:
            continue
        vistos.add(nome)

        link_tag = card.find("a", href=True)
        url_perfil = _normalizar_url(link_tag["href"] if link_tag else None, url_base)

        # Heurística simples: o primeiro <p> ou <span> curto após o nome
        # costuma ser o segmento ou a descrição curta.
        descricao_tag = card.find("p")
        descricao = _texto_de(descricao_tag)

        startups.append(
            StartupCubo(
                nome=nome,
                segmento=None,  # a confirmar com a estrutura real
                descricao_curta=descricao,
                url_perfil=url_perfil,
            )
        )

    return startups


def coletar_vitrine_cubo(salvar: bool = True) -> list[StartupCubo]:
    """
    Busca a vitrine de startups do Cubo Itaú e extrai a lista de
    empresas. Salva o resultado em disco (data/raw/_cubo/) com
    rastreabilidade, se `salvar=True`.
    """
    logger.info("Buscando vitrine de startups do Cubo Itaú: %s", URL_VITRINE_CUBO)

    try:
        resposta = requests.get(URL_VITRINE_CUBO, headers=HEADERS, timeout=15)
        resposta.raise_for_status()
    except requests.RequestException as exc:
        logger.error("Falha ao buscar a vitrine do Cubo: %s", exc)
        return []

    startups = extrair_startups_do_html(resposta.text)
    logger.info("Startups extraídas: %d", len(startups))

    if salvar and startups:
        DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        caminho = DATA_RAW_DIR / f"vitrine_cubo_{timestamp}.json"
        caminho.write_text(
            json.dumps([s.to_dict() for s in startups], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info("Lista de startups salva em: %s", caminho)

    return startups


if __name__ == "__main__":
    coletar_vitrine_cubo()
