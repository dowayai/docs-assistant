from src import config, rag


def test_fr07_refusal_does_not_call_llm(monkeypatch):  # FR-07 AC1
    monkeypatch.setattr(rag, "_search", lambda q: [])
    called = []
    res = rag.answer("питання поза межами", llm=lambda p: called.append(p) or "x")
    assert res["answer"] == config.NO_ANSWER and not called


def test_fr06_prompt_numbers_sources():  # FR-06 (підготовка цитувань)
    hits = [{"text": "t", "source": "a.md", "section": "S", "distance": 0.1}]
    assert "[1] (a.md, S)" in rag.build_prompt("q?", hits)
