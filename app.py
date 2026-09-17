"""
app.py
------
Streamlit UI for ResumeRAG: upload a resume, get a transparent rule-based
ATS score, and chat with an assistant whose answers are grounded (via RAG)
in your actual resume content. Everything runs locally — no API key needed.

Run with:  streamlit run app.py
"""

import streamlit as st

from resume_parser import extract_text
from text_chunker import chunk_resume
from rag_engine import RAGEngine
from ats_scorer import score_resume
from llm_engine import LocalLLM, MODEL_OPTIONS, DEFAULT_MODEL_LABEL

st.set_page_config(page_title="ResumeRAG — AI Resume Feedback", page_icon="📄", layout="wide")


# --- Cached, shareable resources (safe: these hold no per-user data) --------
@st.cache_resource(show_spinner="Loading local language model — first run may take a minute...")
def get_llm(model_name: str) -> LocalLLM:
    llm = LocalLLM(model_name)
    llm.load()
    return llm


# --- Session state (per-user data: resume text, index, chat history) --------
def init_state():
    defaults = {
        "analyzed": False,
        "resume_name": None,
        "ats_result": None,
        "rag_engine": None,
        "chat_history": [],
        "selected_model_label": DEFAULT_MODEL_LABEL,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def analyze_resume(uploaded_file):
    text = extract_text(uploaded_file)
    if not text.strip():
        st.error(
            "Couldn't extract any text from that file — try a different "
            "export (e.g. a text-based PDF rather than a scanned image)."
        )
        return

    chunks = chunk_resume(text)
    engine = RAGEngine()
    engine.build_index(chunks)

    st.session_state.resume_name = uploaded_file.name
    st.session_state.rag_engine = engine
    st.session_state.ats_result = score_resume(text)
    st.session_state.chat_history = []
    st.session_state.analyzed = True


def ask_question(question: str):
    engine = st.session_state.rag_engine
    llm = get_llm(MODEL_OPTIONS[st.session_state.selected_model_label])
    retrieved = engine.retrieve(question, top_k=4)
    chunks_for_prompt = [{"section": r.section, "text": r.text} for r in retrieved]

    with st.spinner("Thinking..."):
        answer = llm.generate(chunks_for_prompt, question)

    st.session_state.chat_history.append({"role": "user", "content": question, "sources": []})
    st.session_state.chat_history.append({"role": "assistant", "content": answer, "sources": retrieved})


# --- UI sections --------------------------------------------------------
def render_sidebar():
    with st.sidebar:
        st.header("📄 ResumeRAG")
        st.caption(
            "A retrieval-augmented resume feedback assistant. Runs fully "
            "offline on your machine — your resume never leaves it."
        )

        labels = list(MODEL_OPTIONS.keys())
        st.session_state.selected_model_label = st.selectbox(
            "Language model",
            options=labels,
            index=labels.index(st.session_state.selected_model_label),
            help="Bigger models give better feedback but are slower on CPU and need more RAM.",
        )

        with st.expander("How this works"):
            st.markdown(
                "1. Your resume is parsed and split into sections "
                "(Skills, Experience, Projects, ...).\n"
                "2. Each section is embedded and stored in a local FAISS "
                "vector index.\n"
                "3. The **ATS score** is computed with transparent, "
                "rule-based checks — no LLM guessing involved.\n"
                "4. When you ask a question, the most relevant resume "
                "sections are **retrieved** and passed to a local "
                "open-source LLM as context, so answers stay grounded in "
                "your actual resume instead of generic advice."
            )

        if st.session_state.analyzed:
            st.divider()
            if st.button("🔄 Analyze a different resume", use_container_width=True):
                st.session_state.analyzed = False
                st.session_state.resume_name = None
                st.session_state.ats_result = None
                st.session_state.rag_engine = None
                st.session_state.chat_history = []
                st.rerun()


def render_upload_screen():
    st.title("📄 ResumeRAG — AI Resume Feedback Analyzer")
    st.write(
        "Upload your resume to get a transparent ATS-style score plus a "
        "chat assistant whose answers are grounded in your actual resume "
        "content, not generic advice."
    )
    st.caption("Runs entirely locally — nothing is uploaded to any external API.")

    uploaded_file = st.file_uploader("Upload resume", type=["pdf", "docx", "txt"])
    if uploaded_file and st.button("Analyze Resume", type="primary"):
        with st.spinner("Reading and indexing your resume..."):
            analyze_resume(uploaded_file)
        st.rerun()


def render_ats_tab():
    result = st.session_state.ats_result
    total = result["total_score"]

    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("ATS Score", f"{total} / 100")
        if total >= 80:
            st.success("Strong — likely to parse cleanly through most ATS systems.")
        elif total >= 60:
            st.warning("Decent, but a few gaps are worth fixing.")
        else:
            st.error("Several ATS-friendliness gaps — see the breakdown for specifics.")
        st.caption(f"Word count: {result['word_count']}")

    with col2:
        st.subheader("Breakdown")
        for item in result["breakdown"]:
            st.write(f"**{item['criterion']}** — {item['score']}/{item['max']}")
            st.progress(item["score"] / item["max"] if item["max"] else 0)
            st.caption(item["note"])


def render_chat_tab():
    st.caption("Answers are generated only from retrieved excerpts of your uploaded resume.")

    presets = [
        ("💪 Strengths", "What are the strongest points of this resume?"),
        ("⚠️ Weaknesses", "What are the weakest or most concerning parts of this resume?"),
        ("✨ Improvements", "What specific improvements would make this resume stronger?"),
        ("🔑 Keywords", "What important keywords or skills seem to be missing from this resume?"),
    ]
    cols = st.columns(4)
    for col, (label, question) in zip(cols, presets):
        if col.button(label, use_container_width=True):
            ask_question(question)
            st.rerun()

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg.get("sources"):
                with st.expander("Resume excerpts used for this answer"):
                    for s in msg["sources"]:
                        st.caption(f"[{s.section}] similarity {s.score:.2f}")
                        st.text(s.text[:300])

    question = st.chat_input("Ask about your resume...")
    if question:
        ask_question(question)
        st.rerun()


def main():
    init_state()
    render_sidebar()

    if not st.session_state.analyzed:
        render_upload_screen()
        return

    st.title(f"📄 Analysis: {st.session_state.resume_name}")
    tab1, tab2 = st.tabs(["📊 ATS Score", "💬 Chat with Resume Assistant"])
    with tab1:
        render_ats_tab()
    with tab2:
        render_chat_tab()


if __name__ == "__main__":
    main()