# Phase 6 World Knowledge And Persistent Memory Plan

Status: complete.

Completion summary:

- `docs/phase6_completion_summary.md`

Phase 6 的目标是把 `Pantheon Age` 从“能调用 LLM 的开放世界雏形”推进到“LLM 能拿到正确世界知识，并且世界能记住已经验证过的变化”。

核心原则：

```text
LLM 负责想象力。
程序负责知识检索、记忆边界、可见性、验证和持久化。
```

Phase 6 不追求最终游玩手感，但会保留完整 AI Agent 项目需要的 RAG 骨架：本地 canon 检索、embedding provider、SQLite 向量缓存和后续向量数据库替换边界。

## Stage 6.1 Canon Corpus Split

目标：把人读的世界观文档拆成程序可检索的小型 canon corpus。

工作：

- 新增 `docs/canon/`；
- 将国家、城市、神明、教会、职业、身份、文风、禁区、事实权限拆成独立 Markdown；
- 每个 canon 文件增加简单 metadata；
- 保留 `docs/world_bible.md` 作为人类阅读用总设定集；
- 不把灵感笔记当作世界事实。

完成标准：

- 国家、城市、神明、教会、职业、文风、禁区可以被独立检索；
- 新 canon 文件不替代 `world_bible.md`，只作为 RAG 地基。

## Stage 6.2 Local Canon Retriever

目标：先做一个本地、可测试、无网络的检索器。

工作：

- 新增 `rag/` 包；
- 加载 `docs/canon/*.md`；
- 解析 metadata；
- 切成小 chunk；
- 通过关键词和标题打分返回 top chunks；
- 让 Agentic Runtime 的 context pack 能读取 canon chunks。

完成标准：

- 查询国家、城市、教会、神明、职业、文风、禁区时能返回相关 chunk；
- 不把整本世界观塞进每次 LLM 调用；
- 普通测试不调用网络。

## Stage 6.3 Persistent Memory Schema

目标：把当前 `GameState.agentic_memory` 推向更稳定的持久化结构。

工作：

- 设计 SQLite memory tables；
- 支持 `player_known`、`location`、`npc_known`、`faction`、`secret` 等 bucket；
- 记录 visibility、authority、source_event、confidence；
- 保持 save/load 和 API session 兼容。

完成标准：

- 验证后的记忆能跨 API session 和存档保存；
- hidden memory 不进入玩家可见上下文。

当前进度：

- `phase3_persistence.sqlite_repository.GameSessionRepository` 已新增 `game_memories` 表；
- 保存游戏 session 时，会把 `GameState.agentic_memory` 中的结构化 `MemoryRecord` 同步到 `game_memories`；
- 读取 session 时，会从 `game_memories` 回填 `GameState.agentic_memory`；
- `list_memory_records(game_id, bucket=None, include_hidden=False)` 可按 bucket 查询记忆；
- 默认查询会隐藏 `bucket='secret'` 或 `visibility='system_secret'` 的秘密记忆；
- 旧的 JSON snapshot 仍保留 `agentic_memory`，用于兼容现有存档和本地 CLI 路径。

下一步：

- 让 Agentic Runtime / API 在需要时直接查询 memory repository，而不是只依赖 snapshot；
- 设计 generated fact commit，让临时 NPC、地点、传闻和事件有明确的持久化入口。

## Stage 6.4 Generated Fact Commit

目标：让 LLM 生成的 NPC、地点、传闻、事件可以“被承认”，但不能无验证写入现实。

工作：

- 设计 generated fact proposal；
- 区分 temporary flavor、persistent generated fact、mechanical fact、secret fact；
- 增加 validator；
- 通过 commit layer 写入 memory/persistence。

完成标准：

- 一个临时 NPC 或传闻只有经过 validator 和 commit 才会成为长期世界事实；
- 未提交内容仍然只存在于当前回合。

当前进度：

- 新增 `GeneratedFactProposal`，作为“把临时生成内容提升为长期事实”的显式 proposal；
- 新增 `validate_generated_fact_proposal()`；
- 新增 `agentic_runtime/generated_facts.py`；
- `commit_generated_fact_proposals()` 会先验证 proposal，再转换为 `MemoryCandidate`，最后复用 `commit_memory_candidates()` 写入长期记忆；
- generated fact 必须带 evidence，不能直接来自 `openai-*` / `llm-*` 原始 provider；
- secret generated fact 必须使用 `fact_type='secret'` 和 `visibility='system_secret'`；
- 未经规则提交死亡权限时，generated fact 不能确认“杀死 / 死亡 / 尸体”等事实。

当前边界：

- 临时 NPC / Event / Item 不会自动变成长期事实；
- 只有显式构造 `GeneratedFactProposal` 并通过 validator 的内容才会持久化；
- 生成事实当前先写入 memory store，后续再接入更细的 API / UI 展示和关系接口。

## Stage 6.5 Relationship And Faction Memory

目标：让国家、教会、派系、NPC 态度可以随事件缓慢变化。

工作：

- 将国家关系 signal 接入 memory；
- 增加教会合法性变化、派系压力、NPC 态度记录；
- 关系变化必须有 evidence 和 source_event；
- 不允许 LLM 一句话直接宣布外交现实。

完成标准：

- 关系变化可以积累；
- 可见性和置信度清晰；
- Narrator 只能叙述已提交或可见的关系变化。

当前进度：

- `MEMORY_BUCKETS` 新增 `faction`，`faction_memory` 不再混入 `quest`；
- 新增 `agentic_runtime/relationship_memory.py`；
- 新增 `RelationshipMemorySignal`，支持 `nation`、`church_legality`、`faction_pressure`、`npc_attitude` 四类关系记忆；
- 新增 `validate_relationship_memory_signal()`；
- 新增 `commit_relationship_memory_signals()`，会把通过验证的关系变化写入 `faction_memory` 或 `secret_memory`；
- 新增 `commit_nation_relation_signals()`，将现有 `NationRelationSignal` 接入长期记忆；
- `NationRelationSignal` 现在要求 evidence；
- `memory_retriever.py` 会把 `faction` bucket 中的公开关系记忆放进玩家可见上下文；
- secret relationship memory 进入 hidden context，不会进入玩家可见上下文。

当前边界：

- 关系记忆现在是 evidence-backed memory，不是最终外交数值系统；
- `NationRelationSnapshot` 仍可用于局部关系计算，后续可从 `faction` 记忆中重建或总结；
- LLM 不能直接宣布结盟、宣战、教会合法性变化或 NPC 永久态度，必须通过关系 signal、validator 和 commit。

## Stage 6.6 Memory Summarizer

目标：长会话不让上下文无限增长。

工作：

- 新增 memory summarizer；
- 总结已提交事实，不新增事实；
- 分玩家可见、地点、NPC、派系、隐藏记忆分别总结；
- summarizer 输出仍需验证。

完成标准：

- 长期游玩时 context pack 保持短小；
- hidden memory 不会被总结到玩家可见内容中。

当前进度：

- 新增 `agentic_runtime/memory_summarizer.py`；
- 当前 summarizer 是本地抽取式摘要，只压缩已有 `MemoryRecord` 的 subject/content，不创造新事实；
- `memory_retriever.py` 已接入 summary + recent records 模式；
- 每个 bucket 超过 `memory_record_limit` 时，会输出一条早期摘要，再输出最近几条完整记录；
- `player_known`、`quest`、`faction`、`location` 的摘要进入对应玩家可见上下文；
- `npc_known` 和 `secret` 的摘要只进入 hidden context；
- 普通 runtime serialization 仍不暴露 `hidden_context`。

当前边界：

- 还没有启用 LLM summarizer；
- 还没有把 summary 作为独立持久化记录写回 SQLite；
- 当前目标是控制 context 长度并保留早期事实线索，后续再做可验证的持久化 summary。

## Stage 6.7 Embedding Retriever

目标：补齐完整 RAG 检索所需的 embedding provider 和向量检索边界。

工作：

- 建立 embedding provider 边界；
- 支持本地 deterministic embedding fallback；
- 支持可选 OpenAI embedding provider；
- 支持 SQLite 向量缓存；
- 后续再考虑 pgvector、Chroma、FAISS 或 reranker；
- 继续保留关键词检索作为 fallback。

完成标准：

- embedding / vector 检索能提高相关性；
- 不破坏 visibility、authority 和本地测试边界。

当前进度：

- 新增 `rag/embeddings.py`；
- 新增 `LocalHashEmbeddingProvider`，作为本地、确定性、无网络的 embedding fallback；
- 新增 `OpenAIEmbeddingProvider`，可选调用真实 OpenAI Embeddings API；
- 新增 `rag/vector_store.py`；
- 新增 `SQLiteCanonVectorStore`，把 canon chunk embedding 缓存到本地 SQLite；
- `rag/canon.py` 的 `retrieve_canon_chunks()` 支持 `strategy='keyword' | 'embedding' | 'hybrid' | 'vector' | 'vector_hybrid'`；
- 默认仍为 `keyword`，保证现有运行路径稳定；
- `agentic_runtime/context_pack.py` 支持 `PANTHEON_CANON_RETRIEVAL`：
  - `keyword`：默认关键词/标题/正文检索；
  - `embedding`：本地 hash embedding 检索；
  - `hybrid`：关键词分数 + embedding 分数；
  - `vector`：SQLite 向量缓存检索；
  - `vector_hybrid`：关键词分数 + SQLite 向量缓存分数；
- 无效 retrieval strategy 会回退到 `keyword`；
- `.env.example` 已补充 `PANTHEON_CANON_RETRIEVAL=keyword`、`PANTHEON_EMBEDDING_PROVIDER`、`PANTHEON_OPENAI_EMBEDDING_MODEL` 和 `PANTHEON_VECTOR_DB_PATH`。

当前边界：

- 本地 hash embedding 不是高质量语义模型，只是 provider 边界和 fallback；
- 默认不会调用 OpenAI embeddings，也不会产生网络费用；
- OpenAI embeddings 只有在 `PANTHEON_EMBEDDING_PROVIDER=openai` 时才会调用；
- 当前向量缓存是轻量 SQLite，不是生产级向量数据库；
- 后续可把 provider / store 替换成 OpenAI embeddings、本地 embedding 模型、pgvector、Chroma、FAISS 或 reranker。

## Non-goals

Phase 6 不做：

- 最终 CLI / UI 体验优化；
- 完整成长系统；
- Web UI；
- 生产部署；
- 生产级向量数据库；
- reranker；
- 直接把完整小说或受版权保护文本作为 RAG。
