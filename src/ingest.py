"""FR-01, FR-02: читання документів і поділ на фрагменти."""
import re
from dataclasses import dataclass
from pathlib import Path

from src.config import CHUNK_MAX_CHARS, CHUNK_OVERLAP

SUPPORTED = {".md", ".txt", ".pdf"}


@dataclass
class Chunk:
    text: str
    source: str
    section: str


def read_text(path: Path) -> str:
    ext = path.suffix.lower()
    if ext not in SUPPORTED:  # FR-01 AC2
        raise ValueError(f"Непідтримуваний формат: {ext}. Дозволені: {sorted(SUPPORTED)}")
    if ext == ".pdf":
        from pypdf import PdfReader
        return "\n\n".join(p.extract_text() or "" for p in PdfReader(str(path)).pages)
    return path.read_text(encoding="utf-8")


def _split_long(text: str, max_chars: int, overlap: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    parts, start = [], 0
    while start < len(text):
        parts.append(text[start:start + max_chars])
        start += max_chars - overlap
    return parts


def chunk_text(text: str, source: str, max_chars: int = CHUNK_MAX_CHARS,
               overlap: int = CHUNK_OVERLAP) -> list[Chunk]:
    """Ділить за заголовками Markdown; довгі розділи — на частини з перекриттям."""
    sections, current, path = [], [], ["(початок)"]
    stack: list[tuple[int, str]] = []
    for line in text.splitlines():
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            if "".join(current).strip():
                sections.append((" > ".join(path), "\n".join(current).strip()))
            level, title = len(m.group(1)), m.group(2).strip()
            stack = [s for s in stack if s[0] < level] + [(level, title)]
            path = [t for _, t in stack]
            current = []
        else:
            current.append(line)
    if "".join(current).strip():
        sections.append((" > ".join(path), "\n".join(current).strip()))
    return [Chunk(part, source, sec)
            for sec, body in sections
            for part in _split_long(body, max_chars, overlap)]


def load_file(path: Path) -> list[Chunk]:
    return chunk_text(read_text(path), source=path.name)
