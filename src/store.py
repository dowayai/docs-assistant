"""FR-03, FR-04, FR-05: ембедінги і векторна база (Chroma)."""
import hashlib

import chromadb
from sentence_transformers import SentenceTransformer

from src import config
from src.ingest import Chunk

_model = None


def _embedder() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(config.EMBEDDING_MODEL)
    return _model


def embed_passages(texts: list[str]) -> list[list[float]]:
    # префікси "passage:" / "query:" — вимога моделей родини e5
    return _embedder().encode([f"passage: {t}" for t in texts], normalize_embeddings=True).tolist()


def embed_query(text: str) -> list[float]:
    return _embedder().encode(f"query: {text}", normalize_embeddings=True).tolist()


def collection():
    client = chromadb.PersistentClient(path=config.CHROMA_DIR)
    return client.get_or_create_collection(config.COLLECTION, metadata={"hnsw:space": "cosine"})


def add_chunks(chunks: list[Chunk]) -> int:
    if not chunks:
        return 0
    # NFR-02: детермінований id => повторна індексація не дублює фрагменти
    ids = [hashlib.sha1(f"{c.source}|{c.section}|{c.text}".encode()).hexdigest() for c in chunks]
    collection().upsert(
        ids=ids,
        documents=[c.text for c in chunks],
        embeddings=embed_passages([c.text for c in chunks]),
        metadatas=[{"source": c.source, "section": c.section} for c in chunks],
    )
    return len(chunks)


def search(question: str, k: int = config.TOP_K) -> list[dict]:
    col = collection()
    if col.count() == 0:
        return []
    res = col.query(query_embeddings=[embed_query(question)], n_results=min(k, col.count()))
    return [{"text": d, "distance": dist, **meta}
            for d, dist, meta in zip(res["documents"][0], res["distances"][0], res["metadatas"][0])]
