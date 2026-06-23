#  inicializa o Chroma e fornece função para inserir documentos
from typing import List, Dict
from .config import CHROMA_PERSIST_DIR

def init_chroma(persist_dir: str = CHROMA_PERSIST_DIR):
    """
    Inicializa e retorna um cliente Chroma com persistência DuckDB+Parquet.
    """
    try:
        import chromadb
        from chromadb.config import Settings
    except Exception as e:
        raise RuntimeError("chromadb é necessário: pip install chromadb") from e

    client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=str(persist_dir)))
    return client

def upsert_documents(client, collection_name: str, docs: List[Dict]):
    """
    Insere ou atualiza documentos em uma coleção Chroma.
    Cada item em `docs` deve conter `id`, `text` e opcional `meta` (dict).
    """
    coll = client.get_or_create_collection(name=collection_name)
    ids = [d.get("id") for d in docs]
    texts = [d.get("text") for d in docs]
    metadatas = [d.get("meta", {}) for d in docs]
    coll.add(ids=ids, documents=texts, metadatas=metadatas)