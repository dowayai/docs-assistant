"""Конфігурація (NFR-01). Значення можна перевизначити змінними середовища."""
import os

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-small")
LLM_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-5-5")
CHROMA_DIR = os.getenv("CHROMA_DIR", "data/chroma")
COLLECTION = os.getenv("COLLECTION", "docs")
CHUNK_MAX_CHARS = int(os.getenv("CHUNK_MAX_CHARS", "1200"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))
TOP_K = int(os.getenv("TOP_K", "4"))
MAX_DISTANCE = float(os.getenv("MAX_DISTANCE", "0.45"))  # косинусна відстань; підібрати в eval/
FEEDBACK_PATH = os.getenv("FEEDBACK_PATH", "data/feedback.jsonl")
NO_ANSWER = "Не знайшов відповіді в наданій документації."
