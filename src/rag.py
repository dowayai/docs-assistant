"""FR-06, FR-07: побудова промпту, відмова за браку підстав, виклик LLM."""
from src import config


def _search(question: str) -> list[dict]:
    from src import store  # ледачий імпорт: тести не завантажують модель ембедінгів
    return store.search(question)


SYSTEM = (
    "Ти асистент до технічної документації. Відповідай ЛИШЕ на основі наданих фрагментів. "
    "Після кожного твердження вказуй номер джерела у квадратних дужках, напр. [1]. "
    f"Якщо у фрагментах немає відповіді, напиши дослівно: {config.NO_ANSWER} "
    "Відповідай мовою питання."
)


def build_prompt(question: str, hits: list[dict]) -> str:
    ctx = "\n\n".join(f"[{i}] ({h['source']}, {h['section']})\n{h['text']}"
                      for i, h in enumerate(hits, 1))
    return f"Фрагменти документації:\n\n{ctx}\n\nПитання: {question}"


def call_llm(prompt: str) -> str:
    import anthropic  # ключ береться зі змінної ANTHROPIC_API_KEY
    msg = anthropic.Anthropic().messages.create(
        model=config.LLM_MODEL, max_tokens=800, system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(b.text for b in msg.content if b.type == "text")


def answer(question: str, llm=call_llm) -> dict:
    hits = [h for h in _search(question) if h["distance"] <= config.MAX_DISTANCE]
    if not hits:  # FR-07 AC1: LLM не викликається
        return {"answer": config.NO_ANSWER, "sources": []}
    return {"answer": llm(build_prompt(question, hits)), "sources": hits}
