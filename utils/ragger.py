"""Small, composable PDF-to-OpenSearch ingestion pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import math
import os
from pathlib import Path
from typing import Any, Protocol


class TextParser:
    def extract(self, pdf_bytes: bytes) -> list[str]:
        """Extract page text lazily so importing the API never parses a PDF."""
        from pypdf import PdfReader
        from io import BytesIO

        return [(page.extract_text() or "") for page in PdfReader(BytesIO(pdf_bytes)).pages]


class Filter:
    def apply(self, text: str) -> str:
        return " ".join(text.split())


class TextSplitter:
    def split(self, text: str, size: int = 800) -> list[str]:
        return [text[i : i + size] for i in range(0, len(text), size)] or []


class KeywordExtractor:
    def __init__(self, active: bool = False, algorithm: str = "scikit") -> None:
        self.active = active
        self.algorithm = algorithm

    def extract(self, text: str) -> list[str] | None:
        """Return keywords only when explicitly enabled.

        Optional keyword libraries are imported here rather than during pipeline
        construction, so the default ingestion path has no extra dependency.
        """
        if not self.active:
            return None
        if self.algorithm == "scikit":
            from sklearn.feature_extraction.text import TfidfVectorizer

            vectorizer = TfidfVectorizer(stop_words="english")
            vectorizer.fit_transform([text])
            return list(vectorizer.get_feature_names_out())
        if self.algorithm == "okt":
            from konlpy.tag import Okt

            return list(dict.fromkeys(Okt().nouns(text)))
        raise ValueError("Keyword algorithm must be 'scikit' or 'okt'")


class Embedder:
    def embed(self, text: str) -> list[float]:
        """Create an embedding with the configured OpenAI embedding model."""
        from openai import OpenAI

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            # Allows local pipeline/unit-test setup before an API key is configured.
            return []
        response = OpenAI(api_key=api_key).embeddings.create(
            model=os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            input=text,
        )
        return list(response.data[0].embedding)


class ChunkBuilder:
    def build(
        self,
        *,
        text: str,
        page: int,
        filename: str,
        original_filename: str,
        document_hash: str,
        embedding: list[float],
        keywords: list[str] | None = None,
    ) -> dict[str, Any]:
        chunk = {
            "text": text,
            "page": page,
            "stored_filename": filename,
            "original_filename": original_filename,
            "document_hash": document_hash,
            "embedding": embedding,
        }
        if keywords is not None:
            chunk["keywords"] = keywords
        return chunk


class OpenSearchIndex(Protocol):
    def index_chunks(self, chunks: list[dict[str, Any]]) -> None: ...

    def replace_document(self, *, filename: str, document_hash: str, chunks: list[dict[str, Any]]) -> None: ...

    def search(self, embedding: list[float], top_k: int) -> list[dict[str, Any]]: ...


class InMemoryOpenSearch:
    """A harmless default adapter; replace it with an OpenSearch client in deployment."""
    def __init__(self) -> None:
        self.chunks: list[dict[str, Any]] = []

    def index_chunks(self, chunks: list[dict[str, Any]]) -> None:
        self.chunks.extend(chunks)

    def replace_document(self, *, filename: str, document_hash: str, chunks: list[dict[str, Any]]) -> None:
        self.chunks = [
            chunk
            for chunk in self.chunks
            if not (chunk.get("stored_filename") == filename and chunk.get("document_hash") == document_hash)
        ]
        self.index_chunks(chunks)

    def search(self, embedding: list[float], top_k: int) -> list[dict[str, Any]]:
        def similarity(chunk: dict[str, Any]) -> float:
            candidate = chunk.get("embedding", [])
            if not candidate or len(candidate) != len(embedding):
                return 0.0
            denominator = math.sqrt(sum(value * value for value in candidate)) * math.sqrt(
                sum(value * value for value in embedding)
            )
            return sum(left * right for left, right in zip(candidate, embedding)) / denominator if denominator else 0.0

        return sorted(
            [{**chunk, "similarity_score": similarity(chunk)} for chunk in self.chunks],
            key=lambda chunk: chunk["similarity_score"],
            reverse=True,
        )[:top_k]


@dataclass
class Hasher:
    def digest(self, content: bytes) -> str:
        return sha256(content).hexdigest()


class Ragger:
    """Own the pipeline collaborators and ingest one batch at a time."""
    def __init__(self, opensearch: OpenSearchIndex | None = None) -> None:
        self.text_parser = TextParser()
        self.filter = Filter()
        self.text_splitter = TextSplitter()
        self.keyword_extractor = KeywordExtractor(active=False, algorithm="scikit")
        self.embedder = Embedder()
        self.chunk_builder = ChunkBuilder()
        self.opensearch = opensearch or InMemoryOpenSearch()
        self.hasher = Hasher()

    def search(self, question: str, top_k: int = 3) -> list[dict[str, Any]]:
        """Embed a question and retrieve its closest indexed chunks."""
        return self.opensearch.search(self.embedder.embed(question), top_k)

    def _stored_filename(self, filename: str, document_hash: str, upload_directory: Path) -> str:
        """Choose a stable name without overwriting a different document."""
        original = Path(filename)
        suffix = original.suffix
        stem = original.stem
        for number in range(0, 10000):
            candidate = f"{stem}{suffix}" if number == 0 else f"{stem}_{number}{suffix}"
            path = upload_directory / candidate
            if not path.exists():
                return candidate
            if self.hasher.digest(path.read_bytes()) == document_hash:
                return candidate
        raise RuntimeError(f"Could not allocate a stored filename for {filename}")

    def ingest_many(self, uploads: list[tuple[str, bytes]], upload_directory: Path) -> dict[str, Any]:
        upload_directory.mkdir(parents=True, exist_ok=True)
        records: list[dict[str, Any]] = []
        total_chunks = 0
        for filename, content in uploads:
            document_hash = self.hasher.digest(content)
            stored_filename = self._stored_filename(filename, document_hash, upload_directory)
            path = upload_directory / stored_filename
            path.write_bytes(content)
            chunks: list[dict[str, Any]] = []
            warnings: list[str] = []
            for page, raw_text in enumerate(self.text_parser.extract(content), start=1):
                for text in self.text_splitter.split(self.filter.apply(raw_text)):
                    keywords: list[str] | None = None
                    try:
                        keywords = self.keyword_extractor.extract(text)
                    except Exception as exc:
                        # Keyword enrichment is optional: retain this chunk and
                        # surface the problem on the affected file instead.
                        warning = f"Keyword extraction failed: {exc}"
                        if warning not in warnings:
                            warnings.append(warning)
                    chunks.append(
                        self.chunk_builder.build(
                            text=text,
                            page=page,
                            filename=stored_filename,
                            original_filename=filename,
                            document_hash=document_hash,
                            embedding=self.embedder.embed(text),
                            keywords=keywords,
                        )
                    )
            replace_document = getattr(self.opensearch, "replace_document", None)
            if replace_document is not None:
                replace_document(filename=stored_filename, document_hash=document_hash, chunks=chunks)
            else:
                # Adapters written against the original minimal protocol still work.
                self.opensearch.index_chunks(chunks)
            total_chunks += len(chunks)
            records.append(
                {
                    "original_filename": filename,
                    "stored_filename": stored_filename,
                    "document_hash": document_hash,
                    "status": "completed",
                    "chunks": len(chunks),
                    "warnings": warnings,
                    "error": None,
                }
            )
        return {"status": "completed", "files": records, "total_chunks": total_chunks}
