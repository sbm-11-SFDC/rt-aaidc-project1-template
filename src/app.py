# src/app.py
from __future__ import annotations
import os
os.environ["POSTHOG_DISABLE"] = "true"
os.environ["ANONYMIZED_TELEMETRY"] = "false"

import glob
import logging
import warnings
import re
from typing import List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from .vectordb import VectorDB

# Silence noisy logs/warnings
warnings.filterwarnings("ignore")
logging.getLogger("chromadb").setLevel(logging.ERROR)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


# ---------------------------
# Step 2: Load documents (.txt)
# ---------------------------
def load_documents() -> List[Dict[str, Any]]:
    """
    Read all .txt files from data/ and return:
    [{"content": str, "metadata": {"source": filename}}]
    """
    results: List[Dict[str, Any]] = []
    for fpath in glob.glob(str(DATA_DIR / "*.txt")):
        try:
            text = Path(fpath).read_text(encoding="utf-8").strip()
            if text:
                results.append(
                    {"content": text, "metadata": {"source": Path(fpath).name}}
                )
        except Exception as e:
            print(f"Skipping {fpath}: {e}")
    return results


def normalize_query(q: str) -> str:
    """Simple query normalization: trim, lowercase, collapse whitespace."""
    if not q:
        return q
    q = q.strip().lower()
    q = re.sub(r"\s+", " ", q)
    return q


class RAGApp:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        load_dotenv()
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY missing in .env")

        # Vector DB: now accepts chunk_overlap default 40
        self.vector_db = VectorDB(
            persist_dir="chromadb", collection_name="docs", chunk_size=500, chunk_overlap=40
        )

        # LLM
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=0)

        # ---------------------------
        # Step 6: Prompt template (tighter + explicit behavior)
        # ---------------------------
        template = """You are a helpful assistant. Use ONLY the provided context to answer.
If the answer isn't in the context, say exactly: "I don't have enough information from the documents."

Instructions:
- Answer in 2–4 sentences.
- Be specific; mention concrete tasks or examples from the context.
- If citing, add (source: filename) at most once at the end.

CONTEXT:
{context}

QUESTION:
{question}
"""
        self.prompt_template = ChatPromptTemplate.from_template(template)

    def ingest(self) -> None:
        docs = load_documents()
        if not docs:
            print("No documents found in data/ — add .txt files first.")
            return
        self.vector_db.add_documents(docs)
        print(f"Ingested {len(docs)} document(s).")

    # ---------------------------
    # Step 7: RAG query pipeline (with de-duplicated context & sources)
    # ---------------------------
    def query(self, question: str, n_results: int = 3) -> Dict[str, Any]:
        # normalize for retrieval but keep original for prompt
        question_norm = normalize_query(question)

        # 1) Retrieve
        hits = self.vector_db.search(question_norm, n_results=n_results)
        docs, metas, dists = hits["documents"], hits["metadatas"], hits["distances"]

        # 2) Build context — dedupe by (source, chunk_index)
        labeled = []
        seen = set()
        for d, m in zip(docs, metas):
            source = (m or {}).get("source", "unknown.txt")
            idx = (m or {}).get("chunk_index", -1)
            key = (source, idx)
            if key in seen:
                continue
            seen.add(key)
            labeled.append(f"{d}\n(source: {source})")

        context = "\n\n---\n\n".join(labeled) if labeled else "N/A"

        # 3) Generate — use original question (uncased) in prompt for readability
        prompt = self.prompt_template.format_messages(
            context=context, question=question
        )
        resp = self.llm.invoke(prompt)
        answer = getattr(resp, "content", str(resp))

        # 4) Unique source list for pretty printing
        unique_sources = []
        for m in metas:
            s = (m or {}).get("source", "unknown.txt")
            if s not in unique_sources:
                unique_sources.append(s)

        return {
            "answer": answer,
            "context_docs": docs,
            "context_metas": metas,
            "distances": dists,
            "sources": unique_sources,
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--q", "--question", dest="question", type=str, help="Question")
    parser.add_argument("--no-ingest", action="store_true", help="Skip ingestion")
    parser.add_argument("--k", type=int, default=3, help="Top-k chunks to retrieve")
    parser.add_argument("--model", type=str, default="gemini-2.5-flash", help="LLM model name")
    parser.add_argument("--dump-context", action="store_true", help="Print retrieved chunks")

    args = parser.parse_args()

    app = RAGApp(model_name=args.model)

    if not args.no_ingest:
        app.ingest()

    question = args.question or input("\nAsk a question about your documents: ").strip()
    out = app.query(question, n_results=args.k)

    print("\n--- Answer ---\n")
    print(out["answer"])

    if out.get("sources"):
        print("\n--- Sources ---")
        for s in out["sources"]:
            print("- ", s)

    # ✅ Debug prints go HERE
    if args.dump_context:
        print("\n--- Retrieved Chunks (debug) ---")
        for d, m in zip(out["context_docs"], out["context_metas"]):
            print(f"[{m.get('source','unknown')}, chunk={m.get('chunk_index',-1)}] {d[:200]}...")