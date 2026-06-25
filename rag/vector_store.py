"""SQLite-backed vector cache for canon retrieval.

This is intentionally small and local. It gives the project a real vector
retrieval boundary without forcing an external vector database during early
development.
"""

from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
import os
import sqlite3
import time

from .embeddings import cosine_similarity


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VECTOR_DB_PATH = PROJECT_ROOT / "data" / "canon_vectors.sqlite3"
VECTOR_DB_PATH_ENV_VAR = "PANTHEON_VECTOR_DB_PATH"


@dataclass(frozen=True)
class VectorSearchResult:
    score: float
    chunk_id: str


class SQLiteCanonVectorStore:
    """A tiny SQLite vector cache for canon chunks."""

    def __init__(self, db_path=DEFAULT_VECTOR_DB_PATH):
        self.db_path = Path(db_path)

    def ensure_schema(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS canon_vectors (
                    chunk_id TEXT NOT NULL,
                    provider_name TEXT NOT NULL,
                    body_hash TEXT NOT NULL,
                    source_path TEXT NOT NULL,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    visibility TEXT NOT NULL,
                    tags_json TEXT NOT NULL,
                    body TEXT NOT NULL,
                    dimensions INTEGER NOT NULL,
                    vector_json TEXT NOT NULL,
                    updated_at REAL NOT NULL,
                    PRIMARY KEY (chunk_id, provider_name)
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_canon_vectors_category
                ON canon_vectors (category)
                """
            )
            connection.commit()

    def connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def score_chunks(self, query, chunks, embedding_provider):
        """Return vector scores for the provided chunks.

        Missing or stale vectors are embedded and cached first.
        """
        chunks = tuple(chunks)
        if not chunks:
            return {}

        self.ensure_schema()
        provider_name = get_provider_cache_name(embedding_provider)
        self.upsert_missing_or_stale(chunks, embedding_provider, provider_name)
        query_vector = embedding_provider.embed(query)

        current_ids = {build_chunk_id(chunk) for chunk in chunks}
        scores = {}
        with self.connect() as connection:
            placeholders = ",".join("?" for _ in current_ids)
            rows = connection.execute(
                f"""
                SELECT chunk_id, vector_json
                FROM canon_vectors
                WHERE provider_name = ?
                  AND chunk_id IN ({placeholders})
                """,
                (provider_name, *sorted(current_ids)),
            ).fetchall()

        for row in rows:
            vector = deserialize_vector(row["vector_json"])
            score = cosine_similarity(query_vector, vector) * 10.0
            if score > 0:
                scores[row["chunk_id"]] = score
        return scores

    def upsert_missing_or_stale(self, chunks, embedding_provider, provider_name):
        now = time.time()
        with self.connect() as connection:
            for chunk in chunks:
                chunk_id = build_chunk_id(chunk)
                body_hash = build_chunk_hash(chunk)
                existing = connection.execute(
                    """
                    SELECT body_hash
                    FROM canon_vectors
                    WHERE chunk_id = ? AND provider_name = ?
                    """,
                    (chunk_id, provider_name),
                ).fetchone()
                if existing and existing["body_hash"] == body_hash:
                    continue

                text = build_embedding_text(chunk)
                vector = tuple(float(value) for value in embedding_provider.embed(text))
                connection.execute(
                    """
                    INSERT OR REPLACE INTO canon_vectors (
                        chunk_id,
                        provider_name,
                        body_hash,
                        source_path,
                        title,
                        category,
                        visibility,
                        tags_json,
                        body,
                        dimensions,
                        vector_json,
                        updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        chunk_id,
                        provider_name,
                        body_hash,
                        chunk.source_path,
                        chunk.title,
                        chunk.category,
                        chunk.visibility,
                        json.dumps(list(chunk.tags), ensure_ascii=False),
                        chunk.body,
                        len(vector),
                        serialize_vector(vector),
                        now,
                    ),
                )
            connection.commit()


def build_vector_store_from_env():
    configured_path = os.getenv(VECTOR_DB_PATH_ENV_VAR)
    if configured_path:
        return SQLiteCanonVectorStore(configured_path)
    return SQLiteCanonVectorStore()


def get_provider_cache_name(provider):
    provider_name = getattr(provider, "provider_name", provider.__class__.__name__)
    model = getattr(provider, "model", "")
    dimensions = getattr(provider, "dimensions", "")
    parts = [str(provider_name)]
    if model:
        parts.append(str(model))
    if dimensions:
        parts.append(str(dimensions))
    return ":".join(parts)


def build_chunk_id(chunk):
    raw = f"{chunk.source_path}\n{chunk.title}\n{chunk.category}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def build_chunk_hash(chunk):
    raw = f"{chunk.title}\n{chunk.category}\n{chunk.visibility}\n{'|'.join(chunk.tags)}\n{chunk.body}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def build_embedding_text(chunk):
    return f"{chunk.title}\n{' '.join(chunk.tags)}\n{chunk.body}"


def serialize_vector(vector):
    return json.dumps([float(value) for value in vector], separators=(",", ":"))


def deserialize_vector(raw):
    try:
        return tuple(float(value) for value in json.loads(raw))
    except (TypeError, ValueError, json.JSONDecodeError):
        return ()
