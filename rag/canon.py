"""Deterministic local retrieval over Phase 6 canon Markdown files."""

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import re

from .embeddings import (
    EMBEDDING_KEYWORD_EXPANSIONS,
    LocalHashEmbeddingProvider,
    build_embedding_provider_from_env,
    cosine_similarity,
    tokenize_for_embedding,
)
from .vector_store import build_chunk_id, build_vector_store_from_env


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANON_ROOT = PROJECT_ROOT / "docs" / "canon"
MAX_CHUNK_CHARS = 900
RETRIEVAL_STRATEGIES = ("keyword", "embedding", "hybrid", "vector", "vector_hybrid")


@dataclass(frozen=True)
class CanonChunk:
    """A small, retrievable piece of canon text."""

    title: str
    body: str
    source_path: str
    category: str = "general"
    visibility: str = "public"
    tags: tuple[str, ...] = ()

    def to_dict(self):
        body = self.body
        if len(body) > MAX_CHUNK_CHARS:
            body = body[:MAX_CHUNK_CHARS].rstrip() + "\n[chunk truncated]"
        return {
            "title": self.title,
            "body": body,
            "source_path": self.source_path,
            "category": self.category,
            "visibility": self.visibility,
            "tags": list(self.tags),
        }


def retrieve_canon_chunks(
    query,
    limit=6,
    categories=None,
    canon_root=DEFAULT_CANON_ROOT,
    strategy="keyword",
    embedding_provider=None,
    vector_store=None,
):
    """Return top matching canon chunks for a query.

    `keyword` is the stable default. `embedding` and `hybrid` are Phase 6.7
    provider-boundary paths that remain local and deterministic unless a caller
    passes a different embedding provider.
    """
    if strategy not in RETRIEVAL_STRATEGIES:
        raise ValueError(f"Unsupported canon retrieval strategy: {strategy}")

    allowed_categories = set(categories or [])
    query_terms = extract_query_terms(query)
    chunks = [
        chunk
        for chunk in load_canon_chunks(canon_root)
        if not allowed_categories or chunk.category in allowed_categories
    ]
    query_embedding = None
    provider = embedding_provider
    if strategy in {"embedding", "hybrid"}:
        provider = provider or LocalHashEmbeddingProvider()
        query_embedding = provider.embed(query)
    if strategy in {"vector", "vector_hybrid"}:
        provider = provider or build_embedding_provider_from_env()

    vector_scores = {}
    if strategy in {"vector", "vector_hybrid"}:
        store = vector_store or build_vector_store_from_env()
        vector_scores = store.score_chunks(query, chunks, provider)

    scored = []
    for chunk in chunks:
        score = score_chunk_for_strategy(
            chunk,
            query_terms,
            query,
            strategy,
            provider,
            query_embedding,
            vector_scores,
        )
        if score > 0:
            scored.append((score, chunk))
    scored.sort(key=lambda item: (item[0], item[1].title), reverse=True)
    return [chunk.to_dict() for _, chunk in scored[:limit]]


def score_chunk_for_strategy(
    chunk,
    query_terms,
    query,
    strategy,
    provider,
    query_embedding,
    vector_scores=None,
):
    keyword_score = score_chunk(chunk, query_terms, query)
    if strategy == "keyword":
        return float(keyword_score)

    if strategy in {"vector", "vector_hybrid"}:
        vector_score = (vector_scores or {}).get(build_chunk_id(chunk), 0.0)
        if strategy == "vector":
            return vector_score
        return float(keyword_score) + vector_score

    embedding_score = score_chunk_by_embedding(chunk, provider, query_embedding, query)
    if strategy == "embedding":
        return embedding_score

    # Hybrid keeps exact canon terms strong while letting embedding similarity
    # rescue chunks that use related phrasing.
    return float(keyword_score) + embedding_score


@lru_cache(maxsize=4)
def load_canon_chunks(canon_root=DEFAULT_CANON_ROOT):
    root = Path(canon_root)
    if not root.exists():
        return ()

    chunks = []
    for path in sorted(root.glob("*.md")):
        if path.name == "README.md":
            continue
        text = path.read_text(encoding="utf-8")
        metadata, body = parse_frontmatter(text)
        chunks.extend(chunk_document(path, metadata, body))
    return tuple(chunks)


def parse_frontmatter(text):
    if not text.startswith("---\n"):
        return {}, text.strip()

    _, _, rest = text.partition("---\n")
    metadata_text, separator, body = rest.partition("\n---\n")
    if not separator:
        return {}, text.strip()

    metadata = {}
    for line in metadata_text.splitlines():
        key, separator, value = line.partition(":")
        if separator:
            metadata[key.strip()] = value.strip()
    return metadata, body.strip()


def chunk_document(path, metadata, body):
    category = metadata.get("category", "general")
    visibility = metadata.get("visibility", "public")
    base_title = metadata.get("title") or path.stem
    tags = parse_tags(metadata.get("tags", ""))

    sections = split_markdown_sections(body)
    if not sections:
        return (
            CanonChunk(
                title=base_title,
                body=body,
                source_path=str(path.relative_to(PROJECT_ROOT)),
                category=category,
                visibility=visibility,
                tags=tags,
            ),
        )

    chunks = []
    for heading, section_body in sections:
        title = heading or base_title
        if heading and heading != base_title:
            title = f"{base_title} / {heading}"
        chunks.append(
            CanonChunk(
                title=title,
                body=section_body.strip(),
                source_path=str(path.relative_to(PROJECT_ROOT)),
                category=category,
                visibility=visibility,
                tags=tags,
            )
        )
    return tuple(chunks)


def split_markdown_sections(body):
    sections = []
    current_heading = ""
    current_lines = []

    for line in body.splitlines():
        heading = parse_heading(line)
        if heading:
            if current_lines:
                sections.append((current_heading, "\n".join(current_lines).strip()))
            current_heading = heading
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((current_heading, "\n".join(current_lines).strip()))

    return tuple(section for section in sections if section[1])


def parse_heading(line):
    match = re.match(r"^(#{1,3})\s+(.+?)\s*$", line)
    if not match:
        return ""
    return match.group(2).strip()


def parse_tags(raw_tags):
    tags = []
    for tag in re.split(r"[,，]", raw_tags):
        cleaned = tag.strip()
        if cleaned:
            tags.append(cleaned)
    return tuple(tags)


def extract_query_terms(query):
    query_text = str(query)
    terms = set()
    for token in re.split(r"[\s，。、“”/|:：；;（）()\-]+", query_text):
        token = token.strip()
        if len(token) >= 2:
            terms.add(token)

    for keyword in CANON_KEYWORDS:
        if keyword in query_text:
            terms.add(keyword)
    return terms


def score_chunk(chunk, query_terms, query):
    haystack = f"{chunk.title}\n{' '.join(chunk.tags)}\n{chunk.body}"
    score = 0
    for term in query_terms:
        if not term:
            continue
        if term in chunk.title:
            score += 6
        if term in chunk.tags:
            score += 4
        if term in chunk.body:
            score += 1
    if chunk.title in query:
        score += 8
    return score


def score_chunk_by_embedding(chunk, provider, query_embedding, query):
    if provider is None or query_embedding is None:
        return 0.0
    text = f"{chunk.title}\n{' '.join(chunk.tags)}\n{chunk.body}"
    # Scale cosine into roughly the same range as keyword scores. This is only
    # a local fallback; real embedding providers can tune ranking later.
    return (
        cosine_similarity(query_embedding, provider.embed(text)) * 10.0
        + semantic_expansion_score(query, text)
    )


def semantic_expansion_score(query, haystack):
    score = 0.0
    query_tokens = set(tokenize_for_embedding(query))
    for token in query_tokens:
        expansions = EMBEDDING_KEYWORD_EXPANSIONS.get(token)
        if not expansions:
            continue
        for expansion in expansions:
            if expansion in haystack:
                score += 2.5
    return score


CANON_KEYWORDS = (
    "虚无之壁",
    "混沌海",
    "亚特海",
    "黄金海岸",
    "金门海峡",
    "阿斯特拉山脉",
    "阿尔比昂",
    "卢米埃",
    "瓦尔德",
    "奥斯特",
    "伊斯特亚",
    "诺克提亚",
    "塞勒米亚",
    "罗斯维亚",
    "格兰威克",
    "布莱摩尔",
    "圣维兰",
    "卢塞恩",
    "圣雷米尔",
    "维拉尔",
    "格莱芬",
    "科伦海姆",
    "霍恩维克",
    "维伦纳",
    "卡洛维茨",
    "佩斯塔",
    "阿尔卡萨",
    "贝拉诺",
    "米拉诺",
    "诺克提亚城",
    "萨莱姆",
    "维亚洛夫",
    "海洋之神",
    "真理之神",
    "战争之神",
    "审判之神",
    "丰饶之神",
    "死亡之神",
    "隐秘之神",
    "深渊之神",
    "潮汐圣会",
    "白塔院",
    "铁血教团",
    "审判庭",
    "蔷薇圣庭",
    "安魂教团",
    "夜幕修会",
    "密仪会",
    "欲望母神",
    "骑士",
    "法师",
    "密探",
    "游侠",
    "牧师",
    "炼金术士",
    "线索",
    "物品",
    "死亡",
    "隐藏信息",
    "叙事",
    "文风",
    "维多利亚",
)
