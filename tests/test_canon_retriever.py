import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from rag.canon import load_canon_chunks, retrieve_canon_chunks
from rag.embeddings import LocalHashEmbeddingProvider, build_embedding_provider_from_env, cosine_similarity
from rag.vector_store import SQLiteCanonVectorStore


class CanonRetrieverTests(unittest.TestCase):
    def test_loads_split_canon_chunks(self):
        chunks = load_canon_chunks()

        titles = [chunk.title for chunk in chunks]

        self.assertTrue(any("国家与政治结构" in title for title in titles))
        self.assertTrue(any("八神与教会" in title for title in titles))
        self.assertTrue(any("职业与身份" in title for title in titles))

    def test_retrieves_country_and_strait_context(self):
        results = retrieve_canon_chunks("萨莱姆 密仪会 深渊 金门海峡", limit=4)

        titles = [item["title"] for item in results]

        self.assertLessEqual(len(results), 4)
        self.assertTrue(any("塞勒米亚" in title or "八神与教会" in title for title in titles))
        self.assertTrue(any("金门海峡" in item["body"] or "密仪会" in item["body"] for item in results))

    def test_retrieves_class_context(self):
        results = retrieve_canon_chunks("骑士 退伍军官 护卫 正面战斗", categories=("class",), limit=3)

        self.assertTrue(results)
        self.assertTrue(any("骑士" in item["title"] or "骑士" in item["body"] for item in results))
        self.assertTrue(all(item["category"] == "class" for item in results))

    def test_retrieves_tone_context(self):
        results = retrieve_canon_chunks("煤气灯 报纸 神秘学 调查 文风", categories=("tone",), limit=2)

        self.assertTrue(results)
        self.assertTrue(any("叙事文风" in item["title"] for item in results))

    def test_retrieves_policy_context(self):
        results = retrieve_canon_chunks("不能授予线索 物品 NPC 死亡 隐藏信息", categories=("policy",), limit=4)

        self.assertTrue(results)
        self.assertTrue(any("禁区" in item["title"] or "权限" in item["title"] for item in results))

    def test_results_are_compact(self):
        results = retrieve_canon_chunks("卢塞恩 白塔院 真理 维拉尔", limit=5)

        self.assertTrue(results)
        self.assertTrue(all(len(item["body"]) <= 930 for item in results))

    def test_local_hash_embedding_provider_is_deterministic(self):
        provider = LocalHashEmbeddingProvider(dimensions=32)

        first = provider.embed("萨莱姆 密仪会 金门海峡")
        second = provider.embed("萨莱姆 密仪会 金门海峡")
        unrelated = provider.embed("骑士 护卫 军营")

        self.assertEqual(first, second)
        self.assertGreater(cosine_similarity(first, second), cosine_similarity(first, unrelated))

    def test_embedding_strategy_retrieves_relevant_canon(self):
        provider = LocalHashEmbeddingProvider(dimensions=64)

        results = retrieve_canon_chunks(
            "黑水梦境与深渊祭司",
            limit=4,
            strategy="embedding",
            embedding_provider=provider,
        )

        self.assertTrue(results)
        self.assertTrue(any("深渊" in item["title"] or "密仪会" in item["body"] for item in results))

    def test_hybrid_strategy_preserves_exact_keyword_strength(self):
        results = retrieve_canon_chunks("维拉尔 蔚蓝海岸 港口", limit=3, strategy="hybrid")

        self.assertTrue(results)
        self.assertTrue(any("城市" in item["title"] or "维拉尔" in item["body"] for item in results))

    def test_vector_strategy_uses_sqlite_vector_store(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store = SQLiteCanonVectorStore(Path(temp_dir) / "canon_vectors.sqlite3")
            provider = LocalHashEmbeddingProvider(dimensions=64)

            results = retrieve_canon_chunks(
                "萨莱姆 深渊 金门海峡",
                limit=4,
                strategy="vector",
                embedding_provider=provider,
                vector_store=vector_store,
            )

            self.assertTrue(results)
            self.assertTrue(vector_store.db_path.exists())
            self.assertTrue(any("塞勒米亚" in item["body"] or "深渊" in item["body"] for item in results))

    def test_vector_hybrid_keeps_keyword_signal(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store = SQLiteCanonVectorStore(Path(temp_dir) / "canon_vectors.sqlite3")

            results = retrieve_canon_chunks(
                "白塔院 真理 圣雷米尔",
                limit=3,
                strategy="vector_hybrid",
                vector_store=vector_store,
            )

            self.assertTrue(results)
            self.assertTrue(any("白塔院" in item["body"] or "真理" in item["body"] for item in results))

    def test_embedding_provider_from_env_defaults_to_local(self):
        with patch.dict("os.environ", {"PANTHEON_EMBEDDING_PROVIDER": "local"}):
            provider = build_embedding_provider_from_env()

        self.assertEqual(provider.provider_name, "local-hash-embedding")

    def test_rejects_unknown_retrieval_strategy(self):
        with self.assertRaises(ValueError):
            retrieve_canon_chunks("萨莱姆", strategy="magic")


if __name__ == "__main__":
    unittest.main()
