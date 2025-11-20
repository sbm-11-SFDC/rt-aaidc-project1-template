from __future__ import annotations
from typing import List, Dict, Any, Optional
import uuid
import re
import time

import chromadb
from chromadb import Client
from chromadb.config import Settings

import logging
logging.getLogger("chromadb").setLevel(logging.ERROR)

# Embeddings via Google (uses GOOGLE_API_KEY from .env)
from langchain_google_genai import GoogleGenerativeAIEmbeddings
# If you ever want local (no API) embeddings, see the commented section below.


class VectorDB:
    """
    Thin wrapper around ChromaDB: chunk text, embed chunks, store and search.
    """

    def __init__(
        self,
        persist_dir: Optional[str] = "chromadb",
        collection_name: str = "docs",
        embedding_model: str = "models/text-embedding-004",
        chunk_size: int = 500,
    ):
        self.client: Client = chromadb.Client(
            Settings(
                is_persistent=True if persist_dir else False,
                persist_directory=persist_dir,
            )
        )
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self.chunk_size = chunk_size

        # --- Google hosted embeddings (default) ---
        self.embedding_model = GoogleGenerativeAIEmbeddings(model=embedding_model)

        # --- OPTIONAL: switch to local embeddings (no API calls) ---
        # from langchain_huggingface import HuggingFaceEmbeddings
        # self.embedding_model = HuggingFaceEmbeddings(
        #     model_name="sentence-transformers/all-MiniLM-L6-v2"
        # )

    # ---------------------------
    # Minimal retry helper
    # ---------------------------
    def _retry(self, func, *args, tries: int = 3, base_delay: float = 1.0, **kwargs):
        """
        Retry wrapper with exponential backoff: 1s -> 2s -> 4s.
        Handles transient 504/timeout errors from embedding API.
        """
        last_err = None
        delay = base_delay
        for _ in range(tries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_err = e
                time.sleep(delay)
                delay *= 2
        raise last_err

    # ---------------------------
    # Step 3: Text chunking
    # ---------------------------
    def chunk_text(self, text: str) -> List[str]:
        """
        Sentence-aware chunking into ~chunk_size characters.
        """
        text = (text or "").strip()
        if not text:
            return []

        sentences = re.split(r"(?<=[.!?])\s+", text)
        chunks: List[str] = []
        buf: List[str] = []
        current_len = 0

        for s in sentences:
            s = s.strip()
            if not s:
                continue
            cand = len(s) + (1 if current_len > 0 else 0)
            if current_len + cand <= self.chunk_size:
                buf.append(s)
                current_len += cand
            else:
                if buf:
                    chunks.append(" ".join(buf))
                buf = [s]
                current_len = len(s)

        if buf:
            chunks.append(" ".join(buf))

        # fallback if very small
        if not chunks and text:
            chunks = [text]

        return chunks

    # ---------------------------
    # Step 4: Ingestion
    # ---------------------------
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        documents: [{ "content": str, "metadata": dict }]
        1) chunk each doc  2) embed chunks  3) store in Chroma
        """
        all_ids: List[str] = []
        all_docs: List[str] = []
        all_metas: List[Dict[str, Any]] = []

        for doc in documents:
            content = (doc.get("content") or "").strip()
            meta = doc.get("metadata") or {}
            if not content:
                continue

            chunks = self.chunk_text(content)
            for idx, ch in enumerate(chunks):
                all_ids.append(str(uuid.uuid4()))
                all_docs.append(ch)
                all_metas.append({**meta, "chunk_index": idx, "length": len(ch)})

        if not all_docs:
            return

        # Retry to avoid transient 504s
        embeddings = self._retry(
            self.embedding_model.embed_documents,
            all_docs,
            tries=3,
            base_delay=1.0,
        )

        self.collection.add(
            ids=all_ids,
            documents=all_docs,
            metadatas=all_metas,
            embeddings=embeddings,
        )

    # ---------------------------
    # Step 5: Similarity search
    # ---------------------------
    def search(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Return: {"ids","documents","metadatas","distances"}
        """
        # Retry to avoid transient 504s
        q_emb = self._retry(
            self.embedding_model.embed_query, query, tries=3, base_delay=1.0
        )

        res = self.collection.query(query_embeddings=[q_emb], n_results=n_results)
        return {
            "ids": res.get("ids", [[]])[0],
            "documents": res.get("documents", [[]])[0],
            "metadatas": res.get("metadatas", [[]])[0],
            "distances": res.get("distances", [[]])[0],
        }