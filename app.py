"""FR-08, FR-09: інтерфейс Streamlit."""
import json
import tempfile
import time
from pathlib import Path

import streamlit as st

from src import config, rag, store
from src.ingest import SUPPORTED, load_file

st.set_page_config(page_title="Асистент документації", layout="wide")
st.title("Асистент до технічної документації")

with st.sidebar:
    st.header("Документи")
    files = st.file_uploader("Завантаж файли", type=[e.strip(".") for e in SUPPORTED],
                        accept_multiple_files=True)
    if st.button("Індексувати") and files:
        total = 0
        for f in files:
            with tempfile.TemporaryDirectory() as tmp:
                p = Path(tmp) / f.name
                p.write_bytes(f.getvalue())
                try:
                    total += store.add_chunks(load_file(p))
                except ValueError as e:
                    st.error(str(e))
        st.success(f"Додано/оновлено фрагментів: {total}")
    st.caption(f"У базі фрагментів: {store.collection().count()}")

if "history" not in st.session_state:
    st.session_state.history = []

for i, turn in enumerate(st.session_state.history):
    st.chat_message("user").write(turn["q"])
    with st.chat_message("assistant"):
        st.write(turn["a"]["answer"])
        for n, s in enumerate(turn["a"]["sources"], 1):
            with st.expander(f"[{n}] {s['source']} — {s['section']}"):
                st.write(s["text"])
        c1, c2, _ = st.columns([1, 1, 8])
        for col, label, val in ((c1, "👍", 1), (c2, "👎", -1)):
            if col.button(label, key=f"fb{i}{val}"):
                Path(config.FEEDBACK_PATH).parent.mkdir(parents=True, exist_ok=True)
                with open(config.FEEDBACK_PATH, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps({"q": turn["q"], "a": turn["a"]["answer"], "rating": val},
                                        ensure_ascii=False) + "\n")
                st.toast("Дякую за оцінку")

if q := st.chat_input("Постав питання до документації"):
    t0 = time.time()
    res = rag.answer(q)
    st.session_state.history.append({"q": q, "a": res})
    print(f"[NFR-03] latency={time.time() - t0:.2f}s sources={len(res['sources'])}")  # лог для аналізу
    st.rerun()
