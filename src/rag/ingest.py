import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterator, List
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .config import DATA_PROCESSED, NVIDIA_KB_PROCESSED_DIR, NVIDIA_KB_RAW_DIR

try:
    import trafilatura
except ImportError:  # pragma: no cover - depende do ambiente
    trafilatura = None

logger = logging.getLogger(__name__)

NOISE_PATTERNS = [
    r"^NVIDIA Home$",
    r"^Menu$",
    r"^Menu icon$",
    r"^Close$",
    r"^Close icon$",
    r"^Shopping Cart$",
    r"^Search icon$",
    r"^Click to search$",
    r"^Skip to main content$",
    r"^US$",
    r"^Login$",
    r"^Log In$",
    r"^LogOut$",
    r"^Logout$",
    r"^NVIDIA logo$",
    r"^View All$",
    r"^Load More$",
    r"^Cancel$",
    r"^Accept and Play Video$",
    r"^Alternatively, you can .+watch this video on YouTube.+$",
    r"^Consent for Optional Cookies$",
    r"^Copyright .+ NVIDIA Corporation$",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    )
}

DEFAULT_NVIDIA_URLS = [
    "https://www.nvidia.com/en-us/startups/",
    "https://www.nvidia.com/en-us/ai-data-science/products/nim-microservices/",
    "https://www.nvidia.com/en-us/ai-data-science/products/nemo/",
    "https://developer.nvidia.com/triton-inference-server",
]


@dataclass(frozen=True)
class SourceSpec:
    url: str
    nome_produto: str
    categoria: str
    tags: List[str]
    caso_uso: List[str]
    fonte_tipo: str


SOURCE_SPECS: List[SourceSpec] = [
    SourceSpec(
        url="https://www.nvidia.com/en-us/startups/",
        nome_produto="NVIDIA Inception",
        categoria="programa_startups",
        tags=["startups", "programa", "beneficios", "go-to-market"],
        caso_uso=["aceleracao de startups", "beneficios comerciais e tecnicos"],
        fonte_tipo="official_program",
    ),
    SourceSpec(
        url="https://www.nvidia.com/en-us/ai-data-science/products/nim-microservices/",
        nome_produto="NVIDIA NIM",
        categoria="model_serving",
        tags=["inference", "deployment", "microservices", "llm"],
        caso_uso=["deploy de modelos", "reducao de latencia", "serving em producao"],
        fonte_tipo="official_doc",
    ),
    SourceSpec(
        url="https://www.nvidia.com/en-us/ai-data-science/products/nemo/",
        nome_produto="NVIDIA NeMo",
        categoria="model_customization",
        tags=["training", "fine-tuning", "evaluation", "guardrails"],
        caso_uso=["customizacao de modelos", "avaliacao", "governanca de llms"],
        fonte_tipo="official_doc",
    ),
    SourceSpec(
        url="https://developer.nvidia.com/triton-inference-server",
        nome_produto="Triton Inference Server",
        categoria="inference_infrastructure",
        tags=["inference", "latency", "throughput", "serving"],
        caso_uso=["serving em producao", "otimizacao de inferencia", "batching"],
        fonte_tipo="official_doc",
    ),
]

SOURCE_BY_URL = {spec.url: spec for spec in SOURCE_SPECS}


def load_processed_docs(path: Path = DATA_PROCESSED) -> Iterator[Dict]:
    """
    Itera sobre arquivos JSON em data/processed e retorna dicionarios de documentos.
    """
    if not path.exists():
        logger.warning("Diretorio nao encontrado: %s", path)
        return

    for p in path.rglob("*.json"):
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            logger.warning("JSON invalido em %s: %s", p, exc)
            continue
        except OSError as exc:
            logger.warning("Erro ao ler arquivo %s: %s", p, exc)
            continue

        if isinstance(obj, dict):
            yield obj
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, dict):
                    yield item


def _slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def _spec_for_url(url: str) -> SourceSpec:
    spec = SOURCE_BY_URL.get(url)
    if spec:
        return spec

    parsed = urlparse(url)
    fallback_name = parsed.path.rstrip("/").split("/")[-1] or parsed.netloc
    return SourceSpec(
        url=url,
        nome_produto=fallback_name.replace("-", " ").title(),
        categoria="nvidia_reference",
        tags=["nvidia"],
        caso_uso=["referencia geral"],
        fonte_tipo="official_doc",
    )


def _extract_title(html: str, fallback: str) -> str:
    soup = BeautifulSoup(html, "lxml")

    if soup.title and soup.title.get_text(strip=True):
        return soup.title.get_text(strip=True)

    h1 = soup.find("h1")
    if h1 and h1.get_text(strip=True):
        return h1.get_text(strip=True)

    return fallback


def _extract_main_html(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")

    for selector in ("main", '[role="main"]', "article"):
        node = soup.select_one(selector)
        if node:
            return str(node)

    for selector in (
        ".page",
        ".page-content",
        ".content",
        ".content-main",
        ".nv-article-page",
        ".nv-container",
    ):
        node = soup.select_one(selector)
        if node:
            return str(node)

    return html


def _normalize_lines(text: str) -> str:
    cleaned_lines: List[str] = []
    seen_recent: set[str] = set()

    for raw_line in text.splitlines():
        line = " ".join(raw_line.split()).strip()
        if not line:
            if cleaned_lines and cleaned_lines[-1] != "":
                cleaned_lines.append("")
            continue

        if any(re.match(pattern, line, flags=re.IGNORECASE) for pattern in NOISE_PATTERNS):
            continue
        if len(line) <= 2:
            continue
        if line in seen_recent:
            continue

        cleaned_lines.append(line)
        seen_recent.add(line)
        if len(seen_recent) > 200:
            seen_recent.clear()

    text = "\n".join(cleaned_lines)

    start_markers = [
        "What Is NVIDIA",
        "What is NVIDIA",
        "Overview",
        "NVIDIA NeMo",
        "NVIDIA NIM Microservices",
        "NVIDIA Inception",
        "NVIDIA Dynamo-Triton",
        "Dynamo-Triton",
    ]
    end_markers = [
        "Consent for Optional Cookies",
        "Privacy Policy",
        "Copyright",
    ]

    start_positions = [text.find(marker) for marker in start_markers if text.find(marker) != -1]
    if start_positions:
        text = text[min(start_positions):]

    end_positions = [text.find(marker) for marker in end_markers if text.find(marker) != -1]
    if end_positions:
        text = text[:min(end_positions)]

    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _extract_text(html: str) -> str:
    main_html = _extract_main_html(html)

    if trafilatura is not None:
        text = trafilatura.extract(
            main_html,
            include_comments=False,
            include_links=False,
            include_tables=True,
            favor_recall=False,
            favor_precision=True,
        )
        if text:
            normalized = _normalize_lines(text)
            if normalized:
                return normalized

    soup = BeautifulSoup(main_html, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text("\n", strip=True)
    return _normalize_lines(text)


def _build_document(url: str, html: str) -> Dict:
    spec = _spec_for_url(url)
    titulo = _extract_title(html, spec.nome_produto)
    doc_id = _slugify(spec.nome_produto)
    conteudo = _extract_text(html)

    return {
        "id": doc_id,
        "titulo": titulo,
        "nome_produto": spec.nome_produto,
        "categoria": spec.categoria,
        "conteudo": conteudo,
        "url_pesquisa": url,
        "tags": spec.tags,
        "caso_uso": spec.caso_uso,
        "fonte_tipo": spec.fonte_tipo,
        "coletado_em": datetime.now(timezone.utc).isoformat(),
    }


def collect_url(url: str, timeout: int = 30) -> Dict:
    logger.info("Coletando %s", url)
    response = requests.get(url, headers=HEADERS, timeout=timeout)
    response.raise_for_status()
    return _build_document(url, response.text)


def save_document(doc: Dict, raw_html: str | None = None) -> Path:
    NVIDIA_KB_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output_path = NVIDIA_KB_PROCESSED_DIR / f"{doc['id']}.json"
    output_path.write_text(
        json.dumps(doc, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    if raw_html is not None:
        NVIDIA_KB_RAW_DIR.mkdir(parents=True, exist_ok=True)
        raw_path = NVIDIA_KB_RAW_DIR / f"{doc['id']}.source.html"
        raw_path.write_text(raw_html, encoding="utf-8")

    return output_path


def collect_and_save_urls(urls: List[str]) -> List[Path]:
    saved_paths: List[Path] = []

    for url in urls:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        doc = _build_document(url, response.text)
        saved_paths.append(save_document(doc, raw_html=response.text))
        logger.info("Documento salvo em %s", saved_paths[-1])

    return saved_paths


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    saved = collect_and_save_urls(DEFAULT_NVIDIA_URLS)
    print(f"{len(saved)} documentos salvos em {NVIDIA_KB_PROCESSED_DIR}")
