import pytest
from pathlib import Path

from src.ingest import chunk_text, read_text

MD = "# Інсталяція\nКрок 1.\n\n## Linux\nsudo apt install x\n\n## Windows\n" + ("x" * 3000)


def test_fr02_metadata_and_max_size():  # FR-02 AC1, AC2
    chunks = chunk_text(MD, "doc.md", max_chars=1200, overlap=100)
    assert all(len(c.text) <= 1200 for c in chunks)
    assert all(c.source == "doc.md" and c.section for c in chunks)
    assert any(c.section == "Інсталяція > Linux" for c in chunks)


def test_fr01_unsupported_format(tmp_path: Path):  # FR-01 AC2
    f = tmp_path / "a.docx"
    f.write_text("x")
    with pytest.raises(ValueError):
        read_text(f)
