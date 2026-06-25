# Canon Corpus

`docs/canon/` 是 Phase 6 的 RAG 地基。

它和 `docs/world_bible.md` 的区别：

- `world_bible.md`：给人阅读的总设定集；
- `docs/canon/`：给程序检索的小型世界知识块；
- `docs/inspiration_notes.md`：灵感来源和原创边界，不是世界事实；
- `docs/forbidden_outputs.md`：LLM 禁区和权限边界；
- `docs/tone_guide.md`：叙事风格指南。

每个 canon 文件使用简单 metadata：

```text
---
id: canon.example
title: Example
category: country
visibility: public
tags: tag1, tag2
---
```

字段含义：

- `id`：稳定文档 ID；
- `title`：检索展示标题；
- `category`：知识类型，例如 `geography`、`country`、`city`、`religion`、`class`、`tone`、`policy`；
- `visibility`：默认可见性，目前通常为 `public`；
- `tags`：检索关键词。

原则：

- canon 只写已经确定的世界事实；
- LLM 生成内容不能直接写入 canon；
- 动态关系、临时 NPC、临时地点、传闻和任务变化应进入 memory，而不是改 canon；
- 如果 canon 和旧文档冲突，以 `world_bible.md` 中最新人工确认设定为准，然后同步修订 canon。
