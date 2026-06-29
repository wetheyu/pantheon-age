# 文档总览

这里是 `Pantheon Age` 的文档入口。

README 负责介绍项目；本文件负责告诉你“要看哪份文档”。

## 首先阅读

1. [../AGENTS.md](../AGENTS.md)：工程规则、架构边界、测试命令和协作约束。
2. [project_architecture.md](project_architecture.md)：当前项目结构、运行主链路和模块职责。
3. [final_demo.md](final_demo.md)：最终展示路线、推荐角色、浏览器 demo 步骤和面试讲法。
4. [agentic_runtime_architecture.md](agentic_runtime_architecture.md)：长期 Agentic Runtime 设计。
5. [world_bible.md](world_bible.md)：世界观总览。
6. [github_release_checklist.md](github_release_checklist.md)：上传 GitHub 前的忽略规则、验证命令和公开叙述检查。

## 架构文档

- [project_architecture.md](project_architecture.md)：当前主线架构、目录职责、运行数据流和验证边界。
- [phase1_9_architecture_summary.md](phase1_9_architecture_summary.md)：当前主线、兼容层和历史阶段的边界。
- [agentic_runtime_architecture.md](agentic_runtime_architecture.md)：Intent、Rule Arbiter、Scene、NPC、Event、Item、Memory、Narrator 等 Agent 的职责。
- [llm_runtime_design.md](llm_runtime_design.md)：LLM 提案、验证、提交、叙事和防越权规则。
- [system_design.md](system_design.md)：阶段式系统设计和数据流说明。
- [technical_roadmap.md](technical_roadmap.md)：长期技术栈、性能、部署和工程能力规划。

## 世界观与设定

- [world_bible.md](world_bible.md)：世界设定主文档。
- [canon/](canon/README.md)：供 RAG 检索的拆分设定语料。
- [progression_design.md](progression_design.md)：属性、职业等级、信仰等级、仪式晋升、道具和代价系统。
- [tone_guide.md](tone_guide.md)：叙事文风。
- [forbidden_outputs.md](forbidden_outputs.md)：LLM 禁止越权输出规则。
- [inspiration_notes.md](inspiration_notes.md)：灵感来源和原创边界。
- [rag_seed_cards.md](rag_seed_cards.md)：紧凑设定卡片，作为旧版 fallback。

## 阶段记录

历史或完成记录：

- [phase2_api_plan.md](phase2_api_plan.md)：Phase 2 FastAPI 计划。
- [phase4_llm_runtime_plan.md](phase4_llm_runtime_plan.md)：Phase 4 结构化 LLM Runtime 计划。
- [phase5_agentic_runtime_plan.md](phase5_agentic_runtime_plan.md)：Phase 5 Agentic Runtime 分阶段计划。
- [phase5_completion_summary.md](phase5_completion_summary.md)：Phase 5 完成总结。
- [phase6_world_memory_plan.md](phase6_world_memory_plan.md)：Phase 6 世界知识与长期记忆计划。
- [phase6_completion_summary.md](phase6_completion_summary.md)：Phase 6 完成总结。
- [phase7_completion_summary.md](phase7_completion_summary.md)：Phase 7 最小可玩体验校准完成总结。
- [phase8_progression_plan.md](phase8_progression_plan.md)：Phase 8 成长系统与核心机制计划。
- [phase8_completion_summary.md](phase8_completion_summary.md)：Phase 8 成长系统与核心机制完成总结。
- [phase9_10_execution_plan.md](phase9_10_execution_plan.md)：Phase 9 Web UI/API 与 Phase 10 工程质量执行计划；其中 Phase 9.1 API 合同、Phase 9.2 Web 骨架、Phase 9.3 角色创建流程、Phase 9.4 聊天式游玩界面、Phase 9.5 状态面板和 Phase 9.6 API/Web 综合试玩已完成。
- [final_phase10_plan.md](final_phase10_plan.md)：最终 Phase 10 详细施工计划。
- [dev_setup.md](dev_setup.md)：Phase 10.6 本地开发、运行、测试、环境文件和 Docker 取舍说明。
- [final_demo.md](final_demo.md)：Phase 10.7 最终展示路线、推荐角色、浏览器 demo 步骤和面试讲法。

未来开发：

- [future_phase_plan.md](future_phase_plan.md)：阶段总路线与当前推荐下一步。

## 运行与测试

- [live_llm_testing.md](live_llm_testing.md)：真实 LLM、`.env`、smoke test 和 live test 的安全配置方式。
- [dev_setup.md](dev_setup.md)：推荐开发入口，包括 `scripts/dev.py` 的 `doctor`、`check`、`cli`、`api`、`web-dev`、`web-build` 和 `web-smoke`。
- [github_release_checklist.md](github_release_checklist.md)：发布到 GitHub 前的本地文件、验证命令和提交范围检查。
- [final_demo.md](final_demo.md)：最终 demo 路线和 `scripts/dev.py final-demo` 本地 smoke。
- [playtest_checklist.md](playtest_checklist.md)：Phase 7 世界模式 20 分钟人工试玩清单和本地 fixture 运行方式。
- `tests/test_safety_evals.py`：Phase 10.2 本地安全评测，覆盖奖励、死亡、秘密、旅行、核心神明和资源越权边界。
- `tests/test_narrative_quality_evals.py`：Phase 10.3 本地叙事质量评测，覆盖主持人口吻、具体感、行动钩子、地点锚点和后台词泄露。
- `PANTHEON_PLAY_PROFILE`：Phase 10.4 运行档位，支持 `local`、`fast`、`quality`、`debug`，可配合 `agentic_runtime.smoke_test` 查看速度和预算建议。
- `PANTHEON_OPENAI_PROVIDER` / `PANTHEON_OPENAI_BASE_URL`：Phase 10.5 provider 配置，可在官方 OpenAI 与 Ollama、LM Studio、vLLM 等 OpenAI-compatible 本地端点之间切换。

默认自动化测试必须保持本地、离线、零 API 成本。真实 LLM 和真实 embedding 测试必须通过环境变量显式开启。

## 维护原则

- 世界事实放在 `world_bible.md` 或 `docs/canon/`。
- 工程规则放在 `AGENTS.md`。
- GitHub 发布检查放在 `github_release_checklist.md`。
- 最终 Phase 10 开发计划放在 `final_phase10_plan.md`。
- 已完成阶段的细节放在对应 phase plan / summary。
- 不要在多份文档里重复维护同一条架构规则。
