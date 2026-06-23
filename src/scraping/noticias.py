"""
Coleta de notícias em duas fases (modo "misto"):

Fase 1 (barata): lê a página de listagem e extrai título + resumo/lead
                  de cada notícia, sem nenhuma requisição extra.
Fase 2 (cara):    para cada notícia cujo título+resumo passar o filtro
                  de relevância de IA (src.scraping.relevancia), faz uma
                  requisição extra para buscar o texto completo.

Isso evita gastar requisições de rede (e, mais adiante, chamadas de LLM)
em notícias que claramente não interessam ao escopo do projeto.
"""
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

from src.scraping.fetcher import fetch_page, HEADERS
from src.scraping.relevancia import calcular_score_relevancia_ia

logger = logging.getLogger(__name__)


@dataclass
class ItemNoticia:
    titulo: str
    resumo: str
    url: str
    fonte: str
    relevancia: dict = field(default_factory=dict)
    texto_completo: str | None = None  # só preenchido se vale_aprofundar=True
    coletado_em: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "titulo": self.titulo,
            "resumo": self.resumo,
            "url": self.url,
            "fonte": self.fonte,
            "relevancia": self.relevancia,
            "texto_completo": self.texto_completo,
            "coletado_em": self.coletado_em,
        }


def _texto_de(tag) -> str:
    return tag.get_text(strip=True) if tag else ""


def coletar_listagem_brazil_journal(max_itens: int = 15) -> list[ItemNoticia]:
    """
    Fase 1: lê a listagem de notícias de startups do Brazil Journal e
    extrai título + resumo de cada item, sem abrir as notícias individuais.

    NOTA: os seletores CSS abaixo (article, h2, h3, p) são uma primeira
    tentativa razoável para um blog/CMS de notícias padrão. Se a estrutura
    real do site usar outras classes, este parser pode precisar de ajuste
    fino — nesse caso, o ideal é salvar o HTML bruto (como fazemos no
    script de inspeção do Cubo) e ajustar os seletores com base nele.
    """
    return _coletar_listagem_generica(
        url_listagem="https://braziljournal.com/tag/startups/",
        nome_fonte="Brazil Journal",
        max_itens=max_itens,
    )


def coletar_listagem_neofeed(max_itens: int = 15) -> list[ItemNoticia]:
    """
    Fase 1: lê a página inicial do NeoFeed e extrai título + resumo de
    cada item de notícia visível, mesma lógica do Brazil Journal.

    NeoFeed não tem uma tag específica de "startups" tão clara quanto o
    Brazil Journal, então usamos a home — o filtro de relevância de IA
    (src.scraping.relevancia) é quem faz o trabalho pesado de separar o
    que interessa do que não interessa.
    """
    return _coletar_listagem_generica(
        url_listagem="https://neofeed.com.br/",
        nome_fonte="NeoFeed",
        max_itens=max_itens,
    )


def _coletar_listagem_generica(
    url_listagem: str, nome_fonte: str, max_itens: int
) -> list[ItemNoticia]:
    """
    Lógica compartilhada de parsing de listagem, usada por todas as
    fontes de notícia. Centralizar aqui evita duplicar a mesma lógica
    de extração (article -> h1/h2/h3 -> p) para cada novo site.

    Se uma fonte específica precisar de seletores muito diferentes
    (ex: cards em <div> em vez de <article>), criar uma função própria
    para ela em vez de forçar este parser genérico.
    """
    itens: list[ItemNoticia] = []

    try:
        resposta = requests.get(url_listagem, headers=HEADERS, timeout=10)
        resposta.raise_for_status()
    except requests.RequestException as exc:
        logger.error("Falha ao buscar listagem de %s: %s", nome_fonte, exc)
        return itens

    soup = BeautifulSoup(resposta.text, "lxml")
    blocos = soup.find_all("article")

    if not blocos:
        logger.warning(
            "Nenhum <article> encontrado na listagem de %s. "
            "A estrutura real do site pode ser diferente do esperado — "
            "considere rodar `python -m src.scraping.inspecionar_fontes "
            "--url %s` para revisar os seletores.",
            nome_fonte,
            url_listagem,
        )
        return itens

    for bloco in blocos[:max_itens]:
        link_tag = bloco.find("a", href=True)
        titulo_tag = bloco.find(["h1", "h2", "h3"])
        resumo_tag = bloco.find("p")

        titulo = _texto_de(titulo_tag) or _texto_de(link_tag)
        resumo = _texto_de(resumo_tag)
        url_noticia = link_tag["href"] if link_tag else None

        if not titulo or not url_noticia:
            continue

        # Algumas fontes usam URLs relativas (ex: "/materia/123").
        # Normalizamos para URL absoluta usando o domínio da listagem.
        if url_noticia.startswith("/"):
            base = re.match(r"https?://[^/]+", url_listagem)
            if base:
                url_noticia = base.group(0) + url_noticia

        relevancia = calcular_score_relevancia_ia(f"{titulo} {resumo}")

        itens.append(
            ItemNoticia(
                titulo=titulo,
                resumo=resumo,
                url=url_noticia,
                fonte=nome_fonte,
                relevancia=relevancia,
            )
        )

    return itens


def aprofundar_itens_relevantes(itens: list[ItemNoticia]) -> list[ItemNoticia]:
    """
    Fase 2: para cada item marcado como `vale_aprofundar` pelo filtro de
    relevância, busca o texto completo da notícia. Itens não relevantes
    são retornados sem modificação (sem gastar requisição extra).
    """
    for item in itens:
        if not item.relevancia.get("vale_aprofundar"):
            continue

        logger.info("Aprofundando coleta (sinal de IA encontrado): %s", item.titulo)
        documento = fetch_page(item.url, fonte_tipo="noticia_completa")

        if documento.erro:
            logger.warning("  -> Falha ao buscar texto completo: %s", documento.erro)
        else:
            item.texto_completo = documento.texto

    return itens
