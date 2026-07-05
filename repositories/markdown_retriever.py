from __future__ import annotations

import re
from pathlib import Path


class MarkdownRetriever:
    def __init__(self, docs_dir: str = "docs") -> None:
        self._chunks = self._load_chunks(Path(docs_dir))

    @staticmethod
    def _load_chunks(docs_dir: Path) -> list[str]:
        chunks: list[str] = []
        if not docs_dir.exists():
            return chunks

        for md_file in sorted(docs_dir.glob("*.md")):
            text = md_file.read_text(encoding="utf-8").strip()
            if text:
                chunks.append(text)
        return chunks

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        return set(re.findall(r"\w+", text.lower()))

    def retrieve(self, query: str, top_k: int = 2) -> list[str]:
        if not self._chunks:
            return []
        query_tokens = self._tokenize(query)

        ranked = sorted(
            self._chunks,
            key=lambda chunk: len(query_tokens.intersection(self._tokenize(chunk))),
            reverse=True,
        )
        return ranked[:top_k]
