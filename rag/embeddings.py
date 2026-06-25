"""Embedding provider boundary for local RAG experiments.

This module intentionally starts with a deterministic local provider. It is not
trying to be a high-quality semantic model; it gives the project a stable
interface so OpenAI embeddings, local models, or vector databases can be added
without changing the rest of the retrieval code.
"""

import os
from dataclasses import dataclass
import hashlib
import math
import re

from llm_runtime.providers import OpenAIProviderError, build_openai_client, load_local_env


DEFAULT_EMBEDDING_DIMENSIONS = 128
EMBEDDING_PROVIDER_ENV_VAR = "PANTHEON_EMBEDDING_PROVIDER"
OPENAI_EMBEDDING_MODEL_ENV_VAR = "PANTHEON_OPENAI_EMBEDDING_MODEL"
DEFAULT_OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"


@dataclass(frozen=True)
class LocalHashEmbeddingProvider:
    """Deterministic sparse-feature embedding fallback.

    It hashes lexical features into a fixed-size vector. This keeps tests local,
    fast, and network-free while preserving the same provider shape that a real
    embedding model can implement later.
    """

    dimensions: int = DEFAULT_EMBEDDING_DIMENSIONS
    provider_name: str = "local-hash-embedding"

    def embed(self, text):
        vector = [0.0] * self.dimensions
        for token in tokenize_for_embedding(text):
            index = stable_hash(token) % self.dimensions
            vector[index] += token_weight(token)
        return normalize(vector)


@dataclass(frozen=True)
class OpenAIEmbeddingProvider:
    """OpenAI-backed embedding provider.

    This provider is optional and is never used unless configuration explicitly
    selects it. Tests should keep using local providers so ordinary verification
    stays network-free and token-free.
    """

    model: str = DEFAULT_OPENAI_EMBEDDING_MODEL
    client: object = None
    api_key: str | None = None
    provider_name: str = "openai-embedding"

    def embed(self, text):
        client = self.client or build_openai_client(api_key=self.api_key)
        try:
            response = client.embeddings.create(model=self.model, input=str(text))
        except Exception as exc:
            raise OpenAIProviderError(f"OpenAI embedding call failed: {exc}") from exc

        try:
            return tuple(float(value) for value in response.data[0].embedding)
        except (AttributeError, IndexError, TypeError, ValueError) as exc:
            raise OpenAIProviderError("OpenAI embedding response was invalid.") from exc


def build_embedding_provider_from_env():
    """Build the configured embedding provider.

    Defaults to the local deterministic provider. Set
    `PANTHEON_EMBEDDING_PROVIDER=openai` to use the OpenAI embedding API.
    """
    load_local_env()
    provider_name = os.getenv(EMBEDDING_PROVIDER_ENV_VAR, "local").strip().lower()
    if provider_name in {"local", "hash", "local-hash"}:
        return LocalHashEmbeddingProvider()
    if provider_name == "openai":
        model = os.getenv(OPENAI_EMBEDDING_MODEL_ENV_VAR, DEFAULT_OPENAI_EMBEDDING_MODEL)
        return OpenAIEmbeddingProvider(model=model)
    raise ValueError(f"Unsupported embedding provider: {provider_name}")


def tokenize_for_embedding(text):
    text = str(text)
    tokens = []
    for token in re.split(r"[\s，。、“”/|:：；;（）()\-]+", text):
        cleaned = token.strip().lower()
        if len(cleaned) >= 2:
            tokens.append(cleaned)

    # Chinese text often has no spaces. Character n-grams give the local
    # fallback some overlap even when a query is phrased differently.
    compact = re.sub(r"[\s，。、“”/|:：；;（）()\-]+", "", text)
    for size in (2, 3):
        for index in range(0, max(len(compact) - size + 1, 0)):
            token = compact[index : index + size]
            if token.strip():
                tokens.append(token)

    for keyword, expansions in EMBEDDING_KEYWORD_EXPANSIONS.items():
        if keyword in text:
            tokens.extend(expansions)
    return tuple(tokens)


def token_weight(token):
    if len(token) >= 4:
        return 1.4
    if len(token) == 3:
        return 1.15
    return 1.0


def stable_hash(token):
    digest = hashlib.sha1(token.encode("utf-8")).hexdigest()
    return int(digest[:12], 16)


def normalize(vector):
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return tuple(vector)
    return tuple(value / norm for value in vector)


def cosine_similarity(left, right):
    if not left or not right or len(left) != len(right):
        return 0.0
    return sum(a * b for a, b in zip(left, right))


EMBEDDING_KEYWORD_EXPANSIONS = {
    "黑水": ("深渊", "密仪会", "阿比萨恩", "污染"),
    "梦境": ("深渊", "密仪会", "梦魇", "污染"),
    "梦魇": ("深渊", "密仪会", "污染"),
    "祭司": ("教会", "仪式", "信仰"),
    "深渊": ("深渊之神", "密仪会", "阿比萨恩", "污染"),
    "禁忌": ("深渊", "禁书", "污染", "隐藏信息"),
    "白塔": ("白塔院", "真理之神", "档案", "证词"),
    "真理": ("白塔院", "维瑞塔斯", "证词", "档案"),
    "海峡": ("金门海峡", "塞勒米亚", "贸易", "航线"),
    "盐": ("海洋之神", "潮汐圣会", "港口", "海难"),
    "潮": ("海洋之神", "潮汐圣会", "航线", "港口"),
    "医院": ("蔷薇圣庭", "丰饶之神", "生命", "瘟疫"),
    "瘟疫": ("蔷薇圣庭", "丰饶之神", "污染", "生命"),
    "墓": ("安魂教团", "死亡之神", "遗嘱", "亡者"),
    "假名": ("夜幕修会", "隐秘之神", "诺克提亚", "秘密"),
}
