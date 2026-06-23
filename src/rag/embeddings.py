from typing import Sequence, List
from .config import EMBEDDING_MODEL

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None

class EmbeddingClient:
    """
    Cliente simples para gerar embeddings usando sentence-transformers.
    Instancie e chame `embed(texts)` para obter vetores.
    """
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        if SentenceTransformer is None:
            raise RuntimeError("sentence-transformers não está instalado")
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: Sequence[str]) -> List[List[float]]:
        vectors = self.model.encode(list(texts), show_progress_bar=False)
        return vectors.tolist()