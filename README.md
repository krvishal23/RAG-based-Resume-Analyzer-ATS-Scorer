# RAG-based Resume Analyzer & ATS Scorer

> An AI chatbot that reads your resume, scores it against ATS standards, and tells you exactly what to fix — powered by a local, open-source LLM (no API costs).

## 🧠 Overview

ResumeIQ is a Retrieval-Augmented Generation (RAG) based chatbot that analyzes a single resume and provides:
- An ATS (Applicant Tracking System) compatibility score
- A breakdown of strengths in the resume
- Specific, actionable gaps and improvement suggestions

Unlike tools that compare a resume against a job description, ResumeIQ focuses purely on evaluating the resume on its own merits — formatting, keyword usage, structure, clarity, and ATS-friendliness.

Built as a portfolio project to demonstrate practical skills in **RAG pipelines, LLM integration, and full-stack Python development.**

## ✨ Features

- 📄 Upload a resume (PDF/DOCX) and get instant AI feedback
- 🎯 ATS compatibility scoring
- 💪 Strengths identified from your resume content
- ⚠️ Gaps and missing elements flagged
- 💬 Conversational chatbot interface — ask follow-up questions about your resume
- 🔒 Runs fully locally — no data sent to external APIs, no recurring costs
- ⚡ Built with a free, open-source LLM

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| LLM | Open-source local model (e.g., via Ollama — Llama 3 / Mistral) |
| Embeddings | Sentence-Transformers |
| Vector Store | FAISS / ChromaDB |
| RAG Orchestration | LangChain |
| Resume Parsing | PyPDF2 / pdfplumber / python-docx |
| Language | Python |

> ⚠️ Swap in the exact LLM, vector store, and parsing libraries you actually used — the table above lists common defaults for this kind of project.

## ⚙️ How It Works

1. **Upload** – User uploads a resume (PDF or DOCX)
2. **Parse & Chunk** – Resume text is extracted and split into meaningful chunks
3. **Embed & Store** – Chunks are embedded and stored in a local vector database
4. **Retrieve** – On each query, relevant chunks are retrieved
5. **Generate** – The local LLM uses retrieved context to generate ATS scoring, strengths, gaps, and answers to follow-up questions
6. **Respond** – Results are shown in a conversational chatbot UI

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/) (or your chosen local LLM runtime) installed and running

### Installation

```bash
# Clone the repository
git clone https://github.com/krvishal23/resumeiq.git
cd resumeiq

# Create a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

## 📁 Project Structure

```
resumeiq/
├── app.py                  # Streamlit app entry point
├── src/
│   ├── parser.py            # Resume text extraction
│   ├── embeddings.py        # Chunking & embedding logic
│   ├── vector_store.py      # Vector DB setup & retrieval
│   ├── rag_chain.py         # RAG pipeline & LLM prompting
│   └── scorer.py            # ATS scoring logic
├── requirements.txt
└── README.md
```

> Update this to match your actual folder layout.

## 🗺️ Roadmap

- [ ] Resume-vs-Job-Description matching mode
- [ ] Export analysis report as PDF
- [ ] Support for multiple resume formats (LinkedIn export, etc.)
- [ ] Multi-language resume support

## 🤝 Contributing

Contributions, issues, and feature requests are welcome. Feel free to open an issue or submit a pull request.

## 👤 Author

**Vishal**
- GitHub: [@krvishal23](https://github.com/krvishal23)
