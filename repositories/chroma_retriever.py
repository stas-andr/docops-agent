from __future__ import annotations

from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings


class ChromaRetriever:
    def __init__(
        self,
        embeddings: Embeddings,
        docs_dir: str = "docs",
        collection_name: str = "docops-agent-docs",
        top_k: int = 2,
    ) -> None:
        self._top_k = top_k
        texts = self._load_texts(Path(docs_dir))
        self._has_docs = bool(texts)
        if not texts:
            self._vector_store: Chroma | None = None
            return

        self._vector_store = Chroma.from_texts(
            texts=texts,
            embedding=embeddings,
            collection_name=collection_name,
        )

    @staticmethod
    def _load_texts(docs_dir: Path) -> list[str]:
        if not docs_dir.exists():
            return []

        texts: list[str] = []
        for md_file in sorted(docs_dir.glob("*.md")):
            content = md_file.read_text(encoding="utf-8").strip()
            if content:
                texts.append(content)
        return texts

    def retrieve(self, query: str, top_k: int = 2) -> list[str]:
        normalized = query.strip()
        if not normalized or not self._has_docs or self._vector_store is None:
            return []

        documents = self._vector_store.similarity_search(normalized, k=top_k or self._top_k)
        return [document.page_content for document in documents]
