# Асистент до технічної документації (RAG + Spec-Driven Development)

Порядок роботи: `specs/` → план/завдання → `src/` → `tests/` + `eval/`.

## Запуск
    pip install -r requirements.txt
    export ANTHROPIC_API_KEY=...   # або змінити src/rag.py:call_llm на локальну модель
    streamlit run app.py
    pytest
