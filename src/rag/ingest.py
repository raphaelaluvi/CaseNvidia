import logging
from pathlib import Path
from typing import Dict, Iterator # funcao retorna iterador de dicionarios
import json
from .config import DATA_PROCESSED # importa do config

logger = logging.getLogger(__name__)


def load_processed_docs(path: Path = DATA_PROCESSED) -> Iterator[Dict]:
    """
    Itera sobre arquivos JSON em data/processed e retorna dicionários de documentos.
    Espera JSON com pelo menos campos `id` e `text`, ou listas de objetos.
    """
    if not path.exists():
        logger.warning("Diretório não encontrado: %s", path)
        return

    for p in path.rglob("*.json"):
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            logger.warning("JSON inválido em %s: %s", p, e)
            continue
        except OSError as e:
            logger.warning("Erro ao ler arquivo %s: %s", p, e)
            continue

        if isinstance(obj, dict):
            yield obj
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, dict):
                    yield item
                else:
                    logger.warning("Item ignorado (não é dict) em %s: %r", p, item)
        else:
            logger.warning("Formato inesperado em %s: %s", p, type(obj))