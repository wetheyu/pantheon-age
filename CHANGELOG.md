# Changelog

## Unreleased

- Phase 9.7 完成 Phase 1-9 Consolidation And Final Plan：新增 `docs/phase1_9_architecture_summary.md` 作为当前架构基线，替换旧 `docs/phase1_8_architecture_summary.md`；
- 新增 `docs/final_phase10_plan.md`，把最终 Phase 10 拆成 Observability、Agent Safety Evals、Narrative Quality Evals、Cost/Speed Optimization、Provider Strategy、Packaging/Dev Profiles 和 Final Demo Pass；
- 新增 `tests/test_live_agentic_runtime.py`，为当前 Agentic Runtime 主路径补充显式 opt-in 的真实 LLM live test；
- README、docs/README、AGENTS、technical roadmap 和 live LLM testing 文档同步 Phase 1-9 基线、真实 LLM 测试授权规则和最终 Phase 10 计划；
- 将项目版本推进到 `v9.7.0 Phase 9.7 Phase 1-9 Consolidation And Final Plan`，下一阶段进入 Phase 10.1 Observability；
- Phase 9.6 完成 API/Web Playtest Pass：网页试玩界面新增开场行动建议、新建角色入口、游戏结束态处理和故事日志自动滚动；
- 新增 `web_ui/scripts/api-smoke.mjs` 与 `npm run smoke:api`，在 FastAPI 服务运行时可快速检查 `/health`、`/origins`、`/classes`、`/gods`、`POST /games` 和 `POST /games/{game_id}/actions` 的浏览器主链路；
- README、Web README、AGENTS、future phase plan、technical roadmap 和 Phase 9/10 execution plan 更新到 `v9.6.0 Phase 9.6 API/Web Playtest Pass`；
- Phase 9 Web UI/API 产品体验收口，下一阶段进入 Phase 10.1 Observability；
- Phase 9.5 完成 Character And World Panels：网页游玩界面新增只读角色与世界状态侧栏；
- 状态侧栏展示角色身份、HP、SAN、Suspicion、Corruption、当前位置、已访问地点、六属性、旧四维、成长等级、Revelation、Favor、Devotion、技能、天赋、祷告、负担、背包道具和线索；
- 前端类型扩展到完整公开 `GameState.to_public_dict()` 形状，行动返回后状态面板会跟随后端公开状态刷新；
- 背包面板展示道具 affordance 摘要，但不在前端执行道具效果，仍由后端裁定；
- 将项目版本推进到 `v9.5.0 Phase 9.5 Character And World Panels`，下一阶段进入 Phase 9.6 API/Web Playtest Pass；
- Phase 9.4 完成 Chat-Style Play Surface：网页端创建游戏后可以输入玩家行动并调用 `POST /games/{game_id}/actions`；
- 网页端新增故事日志，区分玩家输入、主持人回复、系统错误和“主持人思考中”加载状态；
- 行动响应会更新浏览器中的公开状态，并展示轻量机制摘要，包括是否消耗回合、是否发生检定、提交效果和状态变化；
- 前端默认不请求 debug payload，正常游玩界面不暴露 runtime/debug 信息；
- 将项目版本推进到 `v9.4.0 Phase 9.4 Chat-Style Play Surface`，下一阶段进入 Phase 9.5 Character And World Panels；
- Phase 9.3 完成 Character Creation Flow：网页客户端新增 world-mode 角色创建表单；
- 玩家现在可以在浏览器里选择名字、出身国家、开局城市、民族、职业、信仰和身份背景，并调用 `POST /games` 创建游戏；
- 创建成功后，网页会展示 `game_id`、当前位置、身份摘要和后端返回的 `opening_text` 开场叙事；
- 前端保持规则边界：只收集选择并调用 API，不复制角色规则、掷骰、验证、记忆或状态提交逻辑；
- 将项目版本推进到 `v9.3.0 Phase 9.3 Character Creation Flow`，下一阶段进入 Phase 9.4 Chat-Style Play Surface；
- Phase 9.2 完成 Web App Scaffold：新增 `web_ui/` React + TypeScript + Vite 最小网页客户端；
- 网页客户端现在会读取 `GET /health`、`GET /classes`、`GET /gods` 和 `GET /origins`，展示 API 状态、职业、神明、出身国家、城市和身份背景；
- FastAPI 增加本地开发 CORS 配置，默认允许 `http://localhost:5173` 和 `http://127.0.0.1:5173`；
- 新增 CORS API 测试，确保 Vite 本地开发页面可以访问后端；
- 将项目版本推进到 `v9.2.0 Phase 9.2 Web App Scaffold`，下一阶段进入 Phase 9.3 Character Creation Flow；
- Phase 9.1 完成 API Contract Cleanup：新增 `GET /origins`，前端可读取八个出身国家、城市、民族和常用身份背景；
- `POST /games` 现在支持 `game_mode`、`origin_country_id`、`origin_city`、`origin_ethnicity` 和 `background_id`，可以直接创建 world-mode 游戏并返回 `game_mode` 与 `setup`；
- `POST /games/{game_id}/actions` 保留旧 `response` 字段，同时新增前端友好的 `story`、`state`、`mechanics` 和可选 `debug` 字段；调试信息默认隐藏，只有请求 `include_debug=true` 时返回；
- API 测试补齐 origins、world-mode 建档、行动响应合同、debug 开关和非法出身配置校验；
- 将项目版本推进到 `v9.1.0 Phase 9.1 API Contract Cleanup`，下一阶段进入 Phase 9.2 Web App Scaffold；
- 将 `docs/phase1_6_architecture_summary.md` 升级并改名为 `docs/phase1_8_architecture_summary.md`，把 Phase 1-8 收束为当前架构基线，明确 CLI、API、SQLite、Phase 4 兼容层、Agentic Runtime、RAG/memory、可玩性校准和成长机制的职责边界；
- 新增 `docs/phase9_10_execution_plan.md`，明确 Phase 9 Web UI/API 产品体验和 Phase 10 工程质量/最终体验优化的逻辑结构、阶段任务和完成标准；
- 更新 README、docs/README、AGENTS 和 technical roadmap，将当前状态推进到 `v8.7.0 Phase 8` 完成后，并把下一阶段指向 Phase 9.1 API Contract Cleanup；
- 删除已被合并吸收的 `docs/refactor_plan.md`，避免旧方向文档与当前 Agentic Runtime 主线重复；
- 重写 `docs/future_phase_plan.md`，将 Phase 7-10 拆成 Codex-friendly 小任务：最小可玩体验校准、成长系统与核心机制、Web UI/API 产品体验、工程质量与最终体验优化；
- 新增 `docs/README.md` 中文文档总入口，并将 README 从长开发日志精简为 GitHub 首页式项目概览；
- Phase 7.1 开始并完成 Runtime Latency Baseline：Agentic Runtime 结果新增 `runtime_trace`，记录运行分支、总耗时和分步耗时；
- CLI 在 `PANTHEON_SHOW_RUNTIME=1` 时会显示紧凑 trace 信息，正常试玩输出保持干净；
- 新增 `agentic_runtime.smoke_test`，用于手动检查 Agentic Runtime 当前走本地、Turn Director、fallback、旧 WorldBundle 或 full multi-agent 分支以及每步耗时；
- Phase 7.2 完成 Story Output Calibration：本地 world-mode 叙事、Scene/NPC/Event/Item fallback 文案和高风险行动提示改为玩家可读的主持人叙事，减少“临时/切片/系统没有确认”等工程感表达；
- Turn Director 与 Agentic Narrator prompt 增加玩家可见文本禁用词，避免真实 LLM 路径输出 validator、commit、rule_result、临时内容、世界事实等后台概念；
- Phase 7.3 完成 Opening And First Hook：world-mode 创建角色后会生成结构化 `opening_profile`，根据出身国家、开局城市、职业、信仰、民族和身份生成开场处境、第一异常、身份钩子和自然行动建议；
- `Character.to_public_dict()` 的 origin 现在包含 `opening_profile`，方便后续 API 和 Web UI 复用开局导入信息；
- Phase 7.4 完成 Location And Scene Continuity Pass：world-mode 明确区分城市级 `current_location` 和具体场景 `current_scene_focus`，非移动行动不会让玩家被叙事带到其他地点；
- 城内移动、离开当前场景和跨城旅行请求现在有不同裁定：城内移动只更新具体场景，离开场景回到城市默认街区，跨城旅行只记录出行准备并拒绝直接瞬移；
- Agentic Runtime 本地路径现在先提交场景锚点，再生成 Scene/NPC/Event/Item 素材，避免“前往码头”后仍按旧街区生成内容；
- Turn Director / Rule Arbiter / WorldBundle / Agentic Narrator prompt 与 validator 增加地点权限边界，禁止 world-mode baseline 直接授予 `location_change` / `city_change`；
- world-mode 新增 `current_scene_focus` 具体场景锚点：`current_location` 继续表示城市级位置，`current_scene_focus` 表示玩家当前所在的具体街区、建筑或场景；
- 非移动行动默认保留在当前具体场景中，避免 LLM 叙事把玩家无端写到市场、旅店、码头等新地点；
- 明确“前往/进入/走向/去”等本城移动时，只更新具体场景锚点，不自动改变城市级位置；
- Turn Director / WorldBundle / Agentic Narrator prompt 增加 location continuity 规则，要求主持人尊重当前场景连续性。
- Phase 7.5 完成 Dice And Consequence UX：world-mode 检定现在记录风险类型、风险标签、掷骰差值和分层结果（完全成功 / 小成功 / 代价失败 / 严重失败）；
- 高风险行动的玩家可见检定文本现在显示 d20、属性、行动修正、DC、结果标签、风险标签和差值，只有发生检定时才展示；
- 暴力、社交压迫、潜行/偷窃/逃离和神秘学压力拥有不同后果提交逻辑，避免所有高风险行动都变成同一种“成功/失败”；
- 暴力成功仍只代表优势、压迫或短暂控制，不会自动确认击杀、永久伤害或奖励；神秘学严重失败可能造成 SAN 与 Corruption 压力；
- Phase 7.6 完成 Playtest Checklist And Fixtures：新增 `docs/playtest_checklist.md`，固定 20 分钟世界模式人工试玩路线；
- 新增 `agentic_runtime/playtest_fixtures.py` 和 `tests/test_playtest_fixtures.py`，用本地 Agentic Runtime 自动跑开场、社交、调查、祈祷、旅行和暴力门槛 fixture；
- Playtest fixture 只断言体验安全性质，不绑定具体 LLM 文案：禁止调试词泄露、禁止未提交死亡、禁止误传送、要求高风险行动有掷骰、要求长期记忆随试玩增长；
- 新增 `docs/phase7_completion_summary.md`，正式收束 Phase 7 最小可玩体验校准的目标、完成阶段、可玩基线、剩余粗糙点和 Phase 8 交接边界；
- Phase 7 收口验证已通过本地全量测试、本地 Agentic Runtime smoke test，并通过真实 LLM `turn_director` 分支 smoke test；
- Phase 7.7 完成 Creative GM Mode：新增 `prompts/creative_gm.md` 和 `OpenAICreativeGMProvider`，把真实试玩主路径调整为“LLM 先作为主持人生成玩家可见叙事，程序只用 sidecar 做验证、掷骰、记忆和状态提交”；
- `PANTHEON_CREATIVE_GM_MODE=1` 成为真实 LLM 世界模式推荐开关，runtime trace 会显示 `creative_gm` 分支；
- Creative GM 保留现有安全边界：未授权死亡、物品、线索、城市旅行、阵营变化和成长奖励仍由 Python 拦截；
- 修复 Creative GM 叙事校验失败时掉回后台报告式文本的问题，安全 fallback 不再暴露“叙事人物 1 / 可疑物件 1 / 你的行动很明确”等系统腔标签；死亡校验也不再误伤“没有尸体的海难”“死亡之神”等正常世界观表达；
- 优化 world-mode 新建角色开场：加入第一幕、资源处境和更自然的行动入口，减少设定说明书感；
- 新增 world feasibility guard：调查记者、教会见习等开局身份会带有资源等级；明显超出资源/身份边界的大额购买（如直接买庄园别墅）会被程序拦截为 `feasibility_blocked`，并转化为询价、找担保人、贷款、调查产权纠纷等可玩路线；
- Phase 7 最小可玩体验校准收口，下一阶段进入 Phase 8 成长系统与核心机制；
- Phase 8.1 完成 Character Model Migration：新增六属性 `attributes`、职业等级、信仰等级、神秘阶位、见证值、神眷、虔诚、成长技能、天赋、祷告、代价和成长 flags；
- `Character.to_dict()` / `from_dict()` / `to_public_dict()` 现在支持 Phase 8 成长字段，并能为旧存档自动补齐默认成长数据；
- CLI “状态”输出新增职业等级、信仰等级、神秘阶位、Favor 和 Revelation，`docs/phase8_progression_plan.md` 记录 Phase 8 分阶段路线；
- Phase 8.2 完成 Minimal Class Skills：每个职业新增一个 Lv1 签名技能，并能在匹配的 world-mode 检定中提供小额加成；
- 掷骰结果现在会记录并展示命中的职业技能，例如 `技能：正面战斗基础 +2`，`check_context` 也会携带技能加成来源；
- Agentic Runtime context pack 现在包含六属性、成长状态和职业技能 affordances，方便真实 LLM 主持人理解角色可用手段；
- world-mode 检定新增自然 1 / 自然 20 处理：技能可以提高成功率，但自然 1 仍然会导致严重失败，自然 20 会成为完全成功；
- Phase 8.3 完成 Minimal Faith Talents And Prayers：每位神明新增 Lv1 天赋和 Lv1 祷告基线；
- 天赋现在会在匹配的 world-mode 检定中提供小额被动加成，祷告会消耗 `favor` 并提供主动加成；
- 掷骰结果和 `check_context` 现在会记录 `talent_bonuses`、`prayer_bonuses` 和神眷不足时的 `blocked_prayers`；
- 玩家可见掷骰文本现在会显示天赋/祷告来源，例如 `天赋：临终残响 +1`、`祷告：安魂 +3`；
- 敌对或受限宗教环境中公开祷告会增加 Suspicion 风险，避免信仰能力变成无代价万能按钮；
- Phase 8.4 完成 Generic Check System Migration：world-mode 检定现在会根据 `risk_type + check_stat` 选择六属性 profile；
- 六属性现在通过 `attribute_modifier = (attribute - 10) // 2` 参与 `行动修正`，旧四属性仍保留为兼容桥；
- 掷骰结果和 `check_context` 现在包含 `attribute_profile` 与 `attribute_modifier`，玩家可见文本会显示如 `属性：体魄 15 +2`；
- 职业技能、信仰天赋、祷告和六属性修正现在共用同一条 world-mode modifier 路径，为后续仪式晋升和物品效果打地基；
- Phase 8.5 完成 Ritual Advancement Slice：新增职业等级、信仰等级和第一次神秘阶位晋升的最小提交路径；
- 晋升尝试现在会返回结构化 `advancement` 数据，包含 requirements、costs、rewards 和 denied_reasons；
- 职业晋升 1 -> 2 会消耗 Revelation 并给职业相关六属性 +1，信仰晋升 1 -> 2 会消耗 Revelation/Favor 并给 Devotion +1；
- 第一次神秘晋升 0 -> 1 需要职业等级 2、信仰等级 2、足够 Revelation/Favor，并会写入一个 burden；
- 条件不足的晋升会被拒绝为 `advancement_denied`，并拒绝 `unearned_advancement`、`unearned_level_change` 和 `unearned_attribute_change`；
- Phase 8.6 完成 Items And Relics Slice：新增 `phase1_cli/items.py`，将普通装备、消耗品和未来遗物/诅咒物的规则接口从背包字符串中抽出来；
- 背包物品现在会公开 `item_affordances`，Agentic Runtime context pack 也会携带可用道具的结构化效果；
- world-mode 检定现在支持明确调用道具后的 `item_bonuses`，并会在掷骰结果、`check_context` 和玩家可见文本中显示道具修正来源；
- 消耗品检定会提交 `item_consumed` 并从背包移除，例如撒下 `仪式粉末` 解析异常；
- 直接使用消耗品现在可以通过提交层改变状态，例如喝下 `镇静药剂` 恢复 SAN，且不能凭叙事生成免费道具；
- Phase 8.7 完成 Phase 8 Final Integration：状态页现在显示六属性、职业技能、信仰天赋、祷告、可用道具和晋升状态；
- 帮助文本新增 world-mode Phase 8 示例，说明职业技能、信仰天赋、祷告、道具和晋升如何与规则交互；
- 新增组合流测试，覆盖职业技能 + 信仰天赋 + 祷告 + 道具 + 信仰晋升的连续玩法；
- 新增 `docs/phase8_completion_summary.md`，将 Phase 8 收口为可交付的成长与核心机制基线；

## v6.0.0 - Phase 6 World Knowledge And Persistent Memory

- Phase 6 开始：新增 `docs/phase6_world_memory_plan.md`，将世界知识与长期记忆拆分为 canon corpus、local retriever、persistent memory schema、generated fact commit、relationship/faction memory、memory summarizer 和 embedding retriever 七个阶段；
- Phase 6 完成：新增 `docs/phase6_completion_summary.md`，将 canon corpus、retriever、persistent memory、generated fact commit、relationship memory、memory summarizer、embedding provider 和 SQLite vector cache 收口为 `v6.0.0`；
- 新增 `docs/canon/` canon corpus，将世界地理、国家、城市、八神教会、职业身份、叙事文风、LLM 禁区和事实权限拆成带 metadata 的可检索文档；
- 新增 `rag/canon.py` 本地 deterministic canon retriever，支持加载 `docs/canon/*.md`、解析 metadata、切分 Markdown chunk、按标题/标签/正文打分并返回紧凑结果；
- Agentic Runtime 的 context pack 开始优先使用 Phase 6 canon retriever，旧 `rag_seed_cards.md` 保留为 fallback；
- Phase 6.3 开始：SQLite persistence 新增 `game_memories` 结构化记忆表，保存 session 时同步 `GameState.agentic_memory` 中的 `MemoryRecord`，读取 session 时回填状态记忆，并提供默认隐藏 secret/system_secret 的 `list_memory_records()` 查询接口；
- Phase 6.4 开始：新增 `GeneratedFactProposal`、generated fact validator 和 `commit_generated_fact_proposals()`，为 LLM 生成的 NPC、地点、传闻、事件、组织、关系、物品和秘密提供显式“验证后成为长期事实”的提交入口；
- Generated fact commit 复用现有 memory candidate / memory store 流程，要求 evidence，拒绝直接来自 raw OpenAI/LLM provider 的持久事实，并阻止未经规则授权的死亡事实提交；
- Phase 6.5 开始：新增 `faction` 记忆桶和 `agentic_runtime/relationship_memory.py`，支持国家关系、教会合法性、派系压力、NPC 态度的 evidence-backed relationship memory；
- `NationRelationSignal` 现在要求 evidence，且可通过 `commit_nation_relation_signals()` 写入长期 faction memory；secret relationship memory 会进入 hidden context，不会暴露给玩家可见上下文；
- Phase 6.6 开始：新增 `agentic_runtime/memory_summarizer.py`，以本地抽取式摘要压缩早期 `MemoryRecord`，`memory_retriever.py` 现在按“早期摘要 + 最近完整记录”构造上下文，并保持 secret/npc hidden memory 不进入玩家可见上下文；
- Phase 6.7：新增 `rag/embeddings.py`、`LocalHashEmbeddingProvider` 和可选 `OpenAIEmbeddingProvider`，为本地 fallback、OpenAI embeddings、本地模型或后续向量数据库建立 provider 边界；
- Phase 6.8：新增 `rag/vector_store.py` 和 `SQLiteCanonVectorStore`，把 canon chunk embedding 缓存到本地 SQLite，提供项目内置轻量向量检索地基；
- `retrieve_canon_chunks()` 支持 `keyword`、`embedding`、`hybrid`、`vector`、`vector_hybrid` 五种检索策略，`agentic_runtime/context_pack.py` 可通过 `PANTHEON_CANON_RETRIEVAL` 切换，默认仍为稳定的 `keyword`；
- 新增 `docs/future_phase_plan.md`，将 Phase 6 之后的执行路线合并为“世界知识与长期记忆 -> 最小可玩体验校准 -> 成长系统 -> Web/API 体验 -> 工程质量与最终体验优化”的阶段计划；
- Phase 5 live path 新增 OpenAI Turn Director 默认快速路径：一次结构化调用返回开放行动理解、裁定建议、临时场景、NPC、事件、物件和紧凑叙事，程序随后验证、掷骰、提交状态并在高风险场景补充或回退安全叙事；
- 新增 `PANTHEON_AGENTIC_TURN_DIRECTOR=1`，普通试玩默认使用单调用快速路径；设置为 `0` 可回到旧版 OpenAI Intent + Rule Arbiter + WorldBundle 多调用路径；
- world-mode CLI 默认输出从 Agent 工作报告调整为玩家可读的故事文本；
- 旧版 OpenAI Intent + Rule Arbiter + WorldBundle 路径仍保留为可回退/可调试模式：Intent 负责理解玩家开放行动，Rule Arbiter 按上下文提出 DC、检定属性、目标画像、阻拦和后果，WorldBundle 一次生成场景、NPC、事件、物件和玩家可见叙事；
- 出于试玩速度考虑，`PANTHEON_USE_AGENTIC_LLM=1` 默认配合 Turn Director 使用；`PANTHEON_AGENTIC_FULL_LLM=1` 才改用较慢的 OpenAI NPC/Event/Item/Narrator 分离 Agents；
- `PANTHEON_SHOW_RUNTIME=1` 现在是显示 Agentic Runtime 调试摘要的唯一开关，world-mode 和 LLM 开关本身不再自动展开调试信息；
- world-mode 开局新增常用身份选择、世界背景、角色职业/信仰/国家/身份介绍和行动示例，引导玩家知道自己是谁、在哪、可以做什么；
- world-mode 主循环不再每回合自动打印状态栏；状态、背包、线索等改为通过命令查看；
- CLI 职业显示名与世界观文档对齐：`战士` -> `骑士`，`盗贼` -> `密探`，内部 class_id 保持兼容；
- 本地 Scene/NPC/Event/Item Agent 的默认文本去掉工程化“临时切片/不能成为事实”等玩家不该看到的表达。
- CLI 输入优先使用 `prompt_toolkit`，改善中文输入删除、光标移动和多字节字符编辑问题；可用 `PANTHEON_SIMPLE_INPUT=1` 强制退回原生 `input()`；
- world-mode 高风险暴力行动会触发 d20 检定并显示计算过程，成功也只确认短暂优势和局势升级，不会自动确认击杀；
- Agentic Runtime Narration validator 现在会拒绝未提交死亡权限的“杀死/死亡/尸体”等叙事确认，避免 LLM 把玩家尝试直接写成世界事实。
- 新增 OpenAI Rule Arbiter Agent 和 `prompts/rule_arbiter.md`，允许 LLM 根据目标身份、地点压力和阻拦者动态提议 DC 与后果；程序会验证 DC 范围、属性、死亡越权和数据形状，不合规时回退本地裁定。
- 新增 `agentic_runtime/context_pack.py`，把玩家状态、当前行动、可见记忆和轻量 RAG seed cards 打包为本回合上下文，避免把完整设定文档无脑塞进每次 LLM 调用。
- WorldBundle 输出扩展为 `Scene/NPC/Event/Item/Narration`，默认 live 体验由 LLM 统一生成本回合场景和叙事，本地 Scene/NPC/Event/Item 主要作为 fallback。

## v5.8.0 - Phase 5 Final Integration

Phase 5 最终整合：

- 将当前版本更新为 `v5.8.0 Phase 5 Final Integration`；
- 新增 `docs/phase5_completion_summary.md`，集中总结 Phase 5 的最终架构、已完成能力、边界和非目标；
- 将 `docs/phase5_agentic_runtime_plan.md` 的 `v5.8.0` 标记为完成，并明确 Phase 5 status 为 complete；
- 更新 README、AGENTS、system design、technical roadmap 和 Agentic Runtime 架构说明，使它们统一描述 Phase 5 最终状态；
- 新增服务层端到端测试，覆盖 `handle_player_input()` 进入 world-mode 后的完整 Phase 5 world slice、memory 写入、runtime payload 和公开状态边界；
- 再次确认普通测试不触发真实 LLM 网络调用。

## v5.7.0 - Phase 5 Agentic World Mode Slice

Phase 5 CLI 世界切片：

- 新增 `agentic_runtime/world_slice.py`，集中处理 world-mode 城市、出身、目标和可见记忆摘要；
- world-mode 的本地 Scene / NPC / Event / Item Agents 现在会生成更具体的临时城市切片内容；
- world-mode Narrator 输出 `【世界切片｜城市】`、行动、场景、临时人物、临时事件、可互动物件和边界提示；
- 本地 Memory Curator 会把已提交的 `world_action` 玩家行动作为可见长期记忆保存；
- world-mode 切片会读取可见长期记忆，但仍不会自动授予线索、物品、地点变化、阵营关系变化或成长奖励；
- 新增测试，覆盖世界切片输出、可见记忆参与下一回合、临时物件不进背包、开放行动不改写地点/线索/角色状态。

## v5.6.0 - Phase 5 Memory-integrated Agentic Loop

Phase 5 记忆检索闭环：

- `Memory Retriever` 现在会读取 `GameState.agentic_memory` 中的本地 memory store；
- `player_known` 和 `quest` 桶会进入玩家已知上下文；
- `location` 桶会进入地点上下文；
- `npc_known` 和 `secret` 桶会进入内部 `hidden_context`；
- `MemoryRetrievalResult.to_dict()` 默认不序列化 `hidden_context`，避免秘密记忆出现在 CLI/API runtime payload；
- Secret memory 不会进入 `GameState.to_public_dict()`，也不会被本地 Narrator 输出；
- 新增测试，覆盖可见记忆跨回合检索、秘密记忆隐藏边界和 `GameState.to_dict()` / `from_dict()` 往返后的记忆保留。

## v5.5.0 - Phase 5 Memory Store Baseline

Phase 5 本地记忆存储基线：

- 新增 `MemoryRecord`，表示已经通过验证、可以写入本地 memory store 的结构化记忆；
- 新增 `agentic_runtime/memory_store.py`；
- 本地 memory store 按 `player_known`、`npc_known`、`location`、`quest`、`secret` 分桶保存记忆；
- `GameState` 新增 `agentic_memory`，让本地 memory store 可以跟随存档和 API snapshot 保存；
- `Memory Curator` 现在会把已提交的确定性效果转成 `should_persist=True` 的 `quest_memory`；
- `run_agentic_turn()` 会验证 memory candidates，并且只写入验证通过且允许持久化的候选记忆；
- Memory validator 阻止 `temporary` / `flavor` 记忆持久化；
- Memory validator 阻止直接来自 `openai-*` / `llm-*` provider 的原始生成内容被当作长期事实保存；
- Secret memory 必须使用 `secret_memory + system_secret` 组合，避免秘密内容进入玩家可见桶；
- 新增测试，覆盖 memory store 分桶、secret memory 隔离、非法原始 LLM 记忆拒绝和 Agentic Runtime 回合写入。

## v5.4.0 - Phase 5 LLM-backed World Agents

Phase 5 世界生成 Agent 接入真实模型：

- 新增 `OpenAINPCAgentProvider`，让 NPC Agent 可以在 `PANTHEON_USE_AGENTIC_LLM=1` 时调用 OpenAI 生成临时 NPC 候选；
- 新增 `OpenAIEventAgentProvider`，让 Event Agent 可以调用 OpenAI 生成临时事件候选；
- 新增 `OpenAIItemAgentProvider`，让 Item Agent 可以调用 OpenAI 生成临时物件候选；
- 新增 `NPCOutput`、`EventOutput` 和 `ItemOutput` structured output model；
- 新增 `prompts/npc_agent.md`、`prompts/event_agent.md` 和 `prompts/item_agent.md`；
- `PANTHEON_USE_AGENTIC_LLM=1` 在当时会启用 OpenAI-backed Intent / NPC / Event / Item Agents；当前默认 live 路径已在 Unreleased 中改为 Intent + Rule Arbiter + WorldBundle；
- Rule Arbiter、Memory Retriever、Memory Curator、State Commit 和 Narrator 仍保持本地 provider，继续由程序负责验证、提交、记忆边界和最终现实写入；
- OpenAI NPC / Event / Item Agent 失败时，orchestrator 会按 agent 粒度记录错误并回退到对应本地 provider；
- 新增 fake-client 自动化测试，覆盖 OpenAI world agent provider 输出、validator 路径和 per-agent fallback；
- 普通测试仍不调用真实网络、不消耗 API token。

## v5.3.4 - Phase 5 Dynamic World Relations

Phase 5 动态国家关系接口：

- 将 `docs/world_bible.md` 中的固定国家关系矩阵改为动态建模原则；
- 明确教会合法性是开局初始秩序，不是永远不变的绝对关系；
- 将教会合法性等级从“受限容忍”和“异端风险”拆分表述合并为“受限 / 异端风险”，并将最后一档表述为“敌对异教 / 邪教”；
- 将“友好公开”表述调整为“合法公开”，避免把条约保护误解为政治友好；
- 调整塞勒米亚宗教合法性：密仪会为国教，其他七神教会因列强压力、通商条约、侨民保护和金门海峡贸易需求而合法存在；
- 调整奥斯特宗教合法性：潮汐圣会在帝国港口和海运体系中合法公开，夜幕修会仍保持受限 / 异端风险；
- 根据国家政体、地理、法律需求、军工需求、港口需求和情报风险重新平衡初始教会合法性矩阵；
- 明确阿尔比昂对白塔院和夜幕修会更警惕，卢米埃和伊斯特亚允许审判庭合法公开，瓦尔德允许白塔院参与工程/军工体系，罗斯维亚允许审判庭处理继承和遗嘱秩序；
- 新增测试约束，确保七神教会的初始公开合法分布保持在相近区间，避免某一教会全图通吃；
- 明确世界观只固定国家结构性条件，例如政体、地理、城市、官方信仰、经济利益和地缘压力；
- 明确国家之间当前亲疏、联盟、制裁、外交危机和战争风险属于动态世界状态；
- 新增 `agentic_runtime/world_relations.py`；
- 新增 `NationRelationSignal`，用于表达事件对两国关系的影响；
- 新增 `NationRelationSnapshot`，用于表达某一对国家的当前关系状态；
- 新增国家关系 signal 校验、neutral snapshot 创建和 signal 应用函数；
- 更新 README、world bible、LLM forbidden outputs、LLM runtime design 和 Phase 5 plan；
- 扩展测试，覆盖合法关系信号更新和非法关系信号拒绝。

## v5.3.3 - Phase 5 Origin Culture Relations

Phase 5 出身文化与宗教合法性上下文：

- 奥斯特帝国出身新增民族选择：奥斯特人、佩斯塔人、波西恩人；
- `configure_character_for_game_mode()` 支持 `origin_ethnicity`；
- `Character.to_public_dict()` 的 `origin` 新增 `ethnicity` 和 `church_context`；
- 新增八个可选出身国家的初始本地教会合法性上下文；
- Agentic Runtime memory retrieval 会读取出身民族和本地宗教合法性，供后续 Agent 判断社会风险；
- `docs/world_bible.md` 新增教会合法性矩阵、教会关系矩阵和国家关系速览；
- 更新 README、Phase 5 plan、system design、technical roadmap 和 Agentic Runtime 架构文档；
- 扩展测试，覆盖奥斯特民族选择、塞勒米亚深渊国教例外和 memory context 中的宗教合法性。

## v5.3.2 - Phase 5 Playable Origin Selection

Phase 5 可选出身国家扩展：

- world-mode 出身国家从五大列强扩展为八个重要国家；
- 新增诺克提亚、塞勒米亚苏丹国、罗斯维亚大公国作为可选出身；
- 诺克提亚开放首都兼唯一城市 `诺克提亚城`；
- 塞勒米亚开放首都 `萨莱姆`；
- 罗斯维亚开放首都 `维亚洛夫`；
- 将出身配置从 `GREAT_POWER_ORIGINS` 调整为 `PLAYABLE_ORIGINS`，避免代码语义继续绑定“五大列强”；
- 更新 README、AGENTS、Phase 5 plan、system design、technical roadmap 和 Agentic Runtime 架构文档；
- 扩展测试，覆盖八国出身列表、单城国家开局和 Agentic Runtime memory context。

## v5.3.1 - Phase 5 Great Power Origin Selection

Phase 5 出身与开局城市选择：

- world-mode 创建角色时新增出身国家选择；
- 暂时只开放五大列强：阿尔比昂、卢米埃、瓦尔德、奥斯特、伊斯特亚；
- 每个国家开放三个核心城市作为开局地点；
- 新增出身信息写入 `Character.flags`：`origin_country_id`、`origin_country`、`origin_country_formal_name`、`origin_identity`、`origin_city`；
- `Character.to_public_dict()` 新增 `origin`，方便 API、前端和 Agentic Runtime 读取玩家身份；
- `Memory Retriever` 会把出身国家、身份和开局城市加入 player-known context；
- world-mode 开场文本、状态描述和地点描述不再固定为格兰威克；
- 更新 README、AGENTS 和 `.env.example`；
- 扩展测试，覆盖五大列强出身选择、公开状态导出和 Agent 记忆上下文。

## v5.3.0 - Phase 5 Tutorial World Mode Split

Phase 5 场景分流：

- 新增 `phase1_cli/scenarios.py`，集中管理 tutorial/world-mode 的模式、场景 ID、起始地点、目标和地点描述；
- 新增 `PANTHEON_GAME_MODE=world`，让 CLI 从格兰威克进入 Phase 5 world-mode；
- 默认 `tutorial` 模式仍然保留雾中修道院固定教程场景；
- world-mode 会自动使用 Phase 5 Agentic Runtime，不需要额外设置 `PANTHEON_USE_AGENTIC_RUNTIME=1`；
- 新增 `world_action` 裁定类型，避免开放世界行动被硬塞进旧修道院地图；
- `State Commit Layer` 新增 world-mode 提交流程：记录开放行动和回合，但不自动改写地点、线索、背包或角色状态；
- `GameState.to_public_dict()` 新增 `game_mode`、`scenario_id` 和 `is_world_mode`；
- `story.py` 的开场、状态、目标和地图输出支持 tutorial/world-mode 分流；
- `rule_engine.handle_move()` 对非固定地图地点更加安全，不再要求当前位置一定存在于教程 `LOCATIONS`；
- 更新 README、AGENTS、system design、technical roadmap、Phase 5 plan 和 Agentic Runtime 架构文档；
- 扩展测试，覆盖 world-mode 自动走 Agentic Runtime 和 `world_action` 提交流程。

## v5.2.0 - Phase 5 Temporary World Agents

Phase 5 临时世界生成：

- 新增 `agentic_runtime/npc_agent.py`，生成当前场景中的临时 NPC 候选；
- 新增 `agentic_runtime/event_agent.py`，生成当前场景的临时事件候选；
- 新增 `agentic_runtime/item_agent.py`，生成可观察、可询问、可尝试使用的临时物件候选；
- 新增 `NPCProposal`、`EventProposal` 和 `ItemProposal`；
- 新增 NPC / Event / Item validators，禁止这些临时候选直接授予线索、背包物品、状态修改或长期世界事实；
- 扩展 `AgenticProviders`，加入 NPC Agent、Event Agent 和 Item Agent provider interface；
- 扩展 `run_agentic_turn()`，让 Phase 5 流程变成 Memory -> Intent -> Scene/NPC/Event/Item -> Rule Arbiter -> Validation -> Commit -> Memory Curator -> Narrator；
- Narrator Agent 现在可以把已验证的临时场景、NPC、事件和物件纳入输出文本；
- CLI Phase 5 debug 输出新增 generated 计数；
- 新增 `docs/phase5_agentic_runtime_plan.md`，记录 Phase 5 从 v5.0 到 v5.6 的分阶段计划；
- 更新 README、AGENTS、system design、technical roadmap 和 Agentic Runtime 架构文档；
- 扩展 `tests/test_agentic_runtime.py`，覆盖临时 NPC / Event / Item 的生成、验证和 trace 输出。

## v5.1.0 - Phase 5 Agent Provider Interfaces

Phase 5 provider 化：

- 新增 `agentic_runtime/providers.py`；
- 新增 Phase 5 provider interfaces：Memory Retriever、Intent Agent、Scene Agent、Rule Arbiter、Memory Curator、Narrator Agent；
- 新增 local provider 实现，封装现有 deterministic Agent 函数；
- 新增 `OpenAIIntentAgentProvider`，让 Phase 5 Intent Agent 可以可选调用真实 OpenAI 模型；
- 新增 `prompts/open_action.md`，要求模型输出开放行动 `OpenActionProposal`，不再输出旧 Phase 4 固定 `intent`；
- 新增 `PANTHEON_USE_AGENTIC_LLM=1`，独立控制 Phase 5 LLM-backed agents；
- `run_agentic_turn()` 改为通过 `AgenticProviders` 调用各 Agent；
- OpenAI Intent Agent 失败时自动回退到 local Intent Agent；
- Phase 5 runtime trace 现在记录 provider 信息、模型、fallback reason 和 runtime errors；
- CLI Phase 5 debug 输出 provider 信息；
- 更新 `.env.example`、README、AGENTS、system design、technical roadmap 和 Agentic Runtime 架构文档；
- 扩展 `tests/test_agentic_runtime.py`，使用 fake OpenAI client 验证 OpenAI Intent Agent provider 路径，不消耗真实 API token。

## v5.0.0 - Phase 5 Agentic Runtime Baseline

Phase 5 起步：

- 新增 `agentic_runtime/` 包；
- 新增 `OpenActionProposal`、`TemporaryContentProposal`、`RuleAdjudicationProposal`、`StateCommitProposal`、`MemoryCandidate`、`MemoryRetrievalResult` 和 Phase 5 `NarrationProposal`；
- 新增 local `Intent Agent`，保留玩家开放行动、方法、目标、猜测和请求效果；
- 新增 local `Scene Agent`，生成 `temporary` 场景细节但不能写入世界事实；
- 新增 local `Rule Arbiter Agent`，把开放行动桥接到当前 deterministic rule engine 可执行的行动；
- 新增 `State Commit Layer`，统一调用 `phase1_cli.rule_engine.apply_rule()` 写入游戏现实；
- 新增 local `Memory Retriever` 和 `Memory Curator Agent`，为后续长期记忆系统建立结构化入口；
- 新增 local `Narrator Agent`，基于已提交结果生成输出；
- 新增 Phase 5 validators，检查开放行动、临时内容、裁定、提交和 memory candidates；
- 新增 `PANTHEON_USE_AGENTIC_RUNTIME=1`，可在 CLI 中启用 Phase 5 路径；
- 新增 Phase 5 runtime debug 输出；
- 让 `跳向前厅` 通过开放意图和 Rule Arbiter 桥接为移动，不再通过给 Phase 1 关键词 parser 增加“跳向”补丁解决；
- 更新 `README.md`、`AGENTS.md`、`docs/system_design.md`、`docs/technical_roadmap.md` 和 `docs/agentic_runtime_architecture.md`；
- 新增 `tests/test_agentic_runtime.py`；
- 更新 `tests/test_game_service.py`，普通测试默认禁用真实 LLM 和 Phase 5 runtime，避免误消耗 API token。

方向校准：

- 明确规则引擎的目标是限制“改变现实的权限”，不是限制 LLM 的想象力；
- 新增 `docs/refactor_plan.md`，记录 Creative LLM + Stable Rules 的长期重构方向；
- 新增 `docs/agentic_runtime_architecture.md`，记录长期 Agentic Runtime 架构；
- 将长期运行流程从“固定规则文本 -> LLM 润色”校准为“LLM 生成可能性 -> validators/rules 裁定权限 -> memory 决定持久化 -> LLM 最终叙事”；
- 将 Phase 4 正式收口为真实 LLM CLI runtime，不再继续给旧 `ActionCandidate(intent=...)` 工作流追加 one-off 关键词、别名或 intent 补丁；
- 明确 Phase 5 方向为 Agentic Runtime Baseline：Intent Agent、Scene/NPC/Event/Item Agents、Rule Arbiter Agent、Memory Curator Agent、State Commit Layer、Narrator Agent；
- 明确 Memory Curator Agent 负责判断哪些信息值得保存、丢弃、压缩、检索或隐藏；
- 新增 `.env.example` 和 `docs/live_llm_testing.md`，建立安全的本地 API key 配置、smoke test 和 live LLM test 流程；
- 将 `.env` 加载改为标准库实现，避免依赖未安装的 `python-dotenv`；
- 增加内容权限等级：`flavor`、`temporary`、`persistent`、`mechanical`、`secret`；
- 将本地部署模型纳入长期开发计划，后续以 Ollama、LM Studio、vLLM 或 OpenAI-compatible local endpoint 作为 provider-compatible backend；
- 更新 README、AGENTS、系统设计、技术路线、LLM 运行逻辑和 Phase 4 计划文档。

RAG 与文风整理：

- 新增 `docs/inspiration_notes.md`，记录高层灵感和原创化边界；
- 新增 `docs/tone_guide.md`，整理维多利亚神秘学、工业烟尘、调查节奏和 NPC 对话风格；
- 新增 `docs/forbidden_outputs.md`，记录 LLM 不能越权生成的世界事实、机械结果、隐藏信息和奖励；
- 新增 `docs/rag_seed_cards.md`，把八神、六大职业和国家气质整理为最小 RAG 设定卡；
- 更新 `prompts/narrator.md`，要求 Narrator 使用原创文风和 RAG notes，但不能复刻其他作品或越权改变游戏事实；
- 更新 `README.md`、`AGENTS.md`、`docs/world_bible.md` 和 `docs/llm_runtime_design.md`，接入这些 RAG 辅助文档。

成长系统设计：

- 新增 `docs/progression_design.md`；
- 设计 `职业等级 + 信仰等级 + 仪式晋升 + 道具系统 + 代价系统` 的长期成长模型；
- 规划未来六属性：体魄、灵巧、洞察、学识、意志、共鸣；
- 参考 d20 / BG3 式小数值结构，补充属性分数、属性修正、升级加属性、属性上限、熟练加值、专精、伤害和防御规划；
- 明确 LLM 不能直接授予等级、阶位、技能、天赋、祷告、属性、道具、神眷或见证值；
- 更新 README、AGENTS、world bible、system design、technical roadmap、LLM runtime design、forbidden outputs、rag seed cards 和 narrator prompt。

世界观整理：

- 调整阿尔比昂核心城市分工；
- 明确城市本名 `格兰威克` 与常用称号 `万都之都` 分离，并设定其为阿尔比昂首都、世界最大城市、全球资本流动中心、最大港口和海军决策中心；
- 将阿尔比昂第二核心城市命名为 `黑炉城`，承担工业城市、工人运动和工厂异常功能；
- 将阿尔比昂第三核心城市命名为 `潮钟城`，参考坎特伯雷，作为海洋之神教会总部和潮汐圣会最高圣座；
- 重设卢米埃三大核心城市：`卢塞恩`、`圣雷米尔`、`维拉尔`，并将 `白城`、`真理之城` 作为称号单独记录，同时新增维拉尔的 `蔚蓝海岸` 度假区；
- 重设瓦尔德三大核心城市：`格莱芬`、`科伦海姆`、`霍恩维克`，明确科伦海姆为全世界最大工业区和铁血教团总部，霍恩维克为东南界河城市并承担瓦尔德唯一港口功能；
- 重设奥斯特三大核心城市：`维伦纳`、`卡洛维茨`、`佩斯塔`，删除奥斯特中的俄罗斯参考，明确俄罗斯气质归属于罗斯维亚大公国；
- 新增奥斯特三大民族：`奥斯特人`、`佩斯塔人`、`波西恩人`，并明确维伦纳为音乐之都、审判之都和审判庭总部，卡洛维茨为工业区与波西恩人聚集地，佩斯塔为亚特海港口和佩斯塔人聚集地；
- 将伊斯特亚正式国名定为 `伊斯特亚王冠领`；
- 重设伊斯特亚为商人寡头君主制，明确 `阿尔卡萨` 为首都和王室权力中心，`贝拉诺` 为界河入海口西岸港口、海军核心、丰饶教会总部和商会寡头聚集地，`米拉诺` 为艺术与经济中心和金融寡头聚集地；
- 新增海域结构：西部为混沌海，中部为亚特海，东部为黄金海岸，亚特海与黄金海岸只通过 `金门海峡` 连通；
- 新增世界边界设定：世界边界为 `虚无之壁`，现有文明无法越过，虚无之壁外是无尽虚空和外神所在地；
- 明确混沌海与亚特海之间开口较大，通常可以自由通行，但阿尔比昂可凭借世界第一海军进行封锁；
- 修正北大陆国家方位：阿尔比昂位于西部群岛和混沌海，瓦尔德在北边，卢米埃在西边，伊斯特亚在南边，奥斯特在中东部，塞勒米亚在东南，罗斯维亚在东北；
- 重设塞勒米亚：控制 `金门海峡`，官方信仰为深渊之神，`萨莱姆` 为深渊教会总部，塞勒米亚被其他国家视为异教国家；
- 重设罗斯维亚：政体为大公专制，官方信仰为死亡之神，首都改为 `维亚洛夫`，并作为安魂教团总部；
- 新增 `阿斯特拉山脉` 与山中小国 `诺克提亚`，明确诺克提亚城是首都兼唯一城市，也是夜幕修会总部所在地；
- 将 `诺克提亚` 纳入其他重要国家列表，明确其为中立宗教城国、夜幕修会总部、保密银行和秘密档案中心；
- 明确诺克提亚位于北大陆中心，与卢米埃、瓦尔德、伊斯特亚和奥斯特四国接壤，阿斯特拉山脉也横贯这一中央边境段；
- 将诺克提亚参考扩展为教宗国与瑞士，补充山地中立、保密银行、秘密档案和山地守卫队设定；
- 明确诺克提亚需要特殊手段才能进入，且夜幕修会在诺克提亚城拥有公开大教堂；
- 明确隐秘之神 `诺克缇拉` 为女性神明；
- 明确“海洋之神教会 / 海神教会 / 海洋教会”默认对应 `潮汐圣会`；
- 将城市设定整理为城市本名与常用称号分离的格式，避免把绰号混入正式地名；
- 新增八神教会速览，明确潮汐圣会、白塔院、铁血教团、审判庭、蔷薇圣庭、安魂教团、夜幕修会和密仪会的正式名、俗称和核心概念；
- 根据命名偏好简化教会名：死亡之神教会固定为 `安魂教团`，审判之神教会固定为 `审判庭`，深渊系邪教网络概称为 `密仪会`，战争调整为 `铁血教团`，真理和丰饶分别调整为 `白塔院`、`蔷薇圣庭`；
- 新增外神与伪神设定，当前阶段唯一明确外神为 `欲望母神`，并明确深渊之神属于八神体系但不被列强承认合法，信仰者多以隐秘组织和地下结社存在；
- 同步更新 RAG 设定卡中的阿尔比昂城市与事件素材。

## v4.7.0 - Phase 4 Real LLM CLI Runtime

在 `v4.6.0` Open Generation Proposal Runtime 基础上完成 Phase 4 的真实 LLM 接入，让 CLI 可以通过可选 OpenAI provider 运行，同时保留本地 fallback。

已完成：

- 实现 `OpenAIActionCandidateProvider`；
- 实现 `OpenAINarrationProvider`；
- 新增 `RuntimeProviders`，集中记录当前 action/narration provider、模型和 fallback 原因；
- 新增 `PANTHEON_USE_LLM`：显式启用真实 LLM；
- 新增 `PANTHEON_OPENAI_MODEL`：覆盖默认模型；
- 新增 `PANTHEON_RAG_CHAR_LIMIT`：限制送入 prompt 的最小 RAG notes 长度；
- 新增 `PANTHEON_SHOW_RUNTIME`：在 CLI 展示 Phase 4 runtime 摘要；
- 新增 `PANTHEON_OPENAI_TIMEOUT` 和 `PANTHEON_OPENAI_MAX_OUTPUT_TOKENS`，避免模型调用长时间无反馈；
- 新增 `PANTHEON_PLAIN_PROMPT`，用于规避部分终端中文输入和彩色 prompt 的显示问题；
- 新增 `python -m llm_runtime.smoke_test`，用于确认真实 LLM provider 是否接入成功；
- 将 OpenAI action candidate 输出改为 schema-first：真实模型必须从合法 intent、risk tag 和 skill tag 枚举中选择；
- 移除“把 jump 等词硬编码映射为 move”的 resolver 逻辑，避免用关键词补丁掩盖 LLM schema 问题；
- 新增可选 live LLM 测试 `tests.test_live_openai_provider`，用于真实验证模型是否能把“跳向前厅”归一为 `move`；
- `game_service.py` 接入 `ActionCandidateProvider -> validator -> AdjudicationRequest -> rule_engine -> NarrationProvider -> validator` 链路；
- LLM action candidate 失败时自动回退到 `KeywordActionCandidateProvider`；
- LLM narration 失败或越权时自动回退到 `TemplateNarrationProvider`；
- `GameResponse.to_dict()` 输出 `llm_runtime` 运行时信息；
- CLI 可显示 provider、candidate、adjudication、narration 和 runtime warning；
- `requirements.txt` 新增 `openai`；
- `.gitignore` 忽略 `.env`，避免 API key 进入 GitHub；
- provider 测试使用 fake OpenAI client，不依赖真实网络和真实 API key；
- 更新 README、AGENTS、LLM runtime design、Phase 4 plan、system design 和 technical roadmap；
- 将当前版本更新为 `v4.7.0 Phase 4 Real LLM CLI Runtime`。

## v4.6.0 - Phase 4 Open Generation Proposal Runtime

在 `v4.5.0` Semantic Action And Generic Adjudication 基础上继续推进 Phase 4，把运行时原则明确为开放生成：LLM 可以自由提出地点、NPC、道具、关系、团队、组织、路线、传闻和事件，程序负责验证权限、统一逻辑、长期记忆和机械结果边界。

已完成：

- 新增 `GeneratedContentProposal`；
- 新增 `GENERATED_CONTENT_TYPES`；
- 新增开放生成 content 类型：`location`、`npc`、`item`、`relationship`、`team`、`organization`、`event`、`rumor`、`route`、`quest_hook`、`object`、`scene_detail`；
- `validate_generated_content_proposal()` 支持验证开放生成内容；
- 允许 `flavor` 和 `temporary` 生成内容；
- 拒绝开放生成内容直接改变 inventory、relationship、faction、state、clue 或 persistent canon；
- `ActionCandidate.item` 不再要求必须是预设道具，允许作为生成式候选对象存在；
- 新增 `prompts/open_generation.md`；
- 更新 README、AGENTS、系统设计、技术路线、LLM 运行逻辑和 Phase 4 计划文档；
- 将当前版本更新为 `v4.6.0 Phase 4 Open Generation Proposal Runtime`。

## v4.5.0 - Phase 4 Semantic Action And Generic Adjudication

在 `v4.4.0` Scene And Event Proposals 基础上继续推进 Phase 4，让结构化行动候选保留玩家行动的想象力，并开始建立通用规则裁定请求。

已完成：

- 扩展 `ActionCandidate`，新增 `method`、`desired_outcome`、`risk_tags`、`skill_tags` 和 `assumptions`；
- `candidate_to_action()` 会保留这些语义字段，后续规则层可以读取；
- 非 `move` 行动的 `target` 可以是临时 NPC、物体或交互对象，不再只允许地点名；
- 进一步放开 `move` target：LLM 可以提出临时房间、街道、区域或路线作为候选目标，但这些目标不会自动成为 canon；
- 新增 `llm_runtime/adjudication.py`；
- 新增 `AdjudicationRequest`、`AdjudicationValidation` 和 `AdjudicationResult`；
- 新增通用裁定默认值：旅行、调查、神秘学分析、战斗、祈祷、休息、道具、潜行和社交；
- 新增 risk tag、skill tag 和 possible cost 验证；
- 更新 `prompts/action_candidate.md`，要求 LLM 保留玩家方法、目标、风险、技能标签和玩家猜测；
- 新增 `tests/test_llm_runtime_adjudication.py`；
- 更新 README、AGENTS、系统设计、技术路线、LLM 运行逻辑和 Phase 4 计划文档；
- 将当前版本更新为 `v4.5.0 Phase 4 Semantic Action And Generic Adjudication`。

## v4.4.0 - Phase 4 Scene And Event Proposals

在 `v4.3.0` Structured Action Candidate 基础上继续推进 Phase 4，让 LLM 运行时可以提出局部场景、普通 NPC、传闻和小事件，但仍不能直接改变世界状态。

已完成：

- 新增 `SceneProposal`、`EventProposal` 和 `ProposalValidation`；
- 新增 `AUTHORITY_LEVELS`：`flavor`、`temporary`、`persistent`、`mechanical`、`secret`；
- 新增 `llm_runtime/proposals.py`；
- 当前只允许展示型 `flavor` 和 `temporary` proposal；
- validator 会拒绝 persistent world facts、mechanical state changes、new clues、location movement 和 secret-like claims；
- 新增 `prompts/scene_event.md`；
- 新增 `tests/test_llm_runtime_proposals.py`；
- 更新 README、AGENTS、系统设计、技术路线、LLM 运行逻辑和 Phase 4 计划文档；
- 将当前版本更新为 `v4.4.0 Phase 4 Scene And Event Proposals`。

## v4.3.0 - Phase 4 Structured Action Candidate

在 `v4.2.0` Prompt And Policy Files 基础上继续推进 Phase 4，让 LLM 运行时从“叙事提案”扩展到“行动候选提案”。

已完成：

- 新增 `ActionCandidate`、`ActionCandidateValidation` 和 `ActionCandidateResult`；
- 新增 `llm_runtime/actions.py`；
- 新增行动候选验证：supported intent、known location、known item、confidence 范围；
- 新增 `resolve_action_candidate()`，验证失败时回退到当前关键词 parser；
- 新增 `ActionCandidateProvider`、`KeywordActionCandidateProvider` 和 `OpenAIActionCandidateProvider`；
- 新增 `prompts/action_candidate.md`；
- 新增 `tests/test_llm_runtime_actions.py`；
- 更新 README、AGENTS、系统设计、技术路线和 LLM 运行逻辑文档；
- 将当前版本更新为 `v4.3.0 Phase 4 Structured Action Candidate`。

## v4.2.0 - Phase 4 Prompt And Policy Files

在 `v4.1.0` LLM Provider Interface 基础上继续推进 Phase 4，把 Narrator prompt 和禁止行为从代码中分离出来。

已完成：

- 新增 `prompts/`；
- 新增 `prompts/narrator.md`，记录 Narrator 的输入、输出 schema、允许 claim 和禁止行为；
- 新增 `llm_runtime/prompts.py`；
- 新增 `load_prompt()`、`list_prompt_names()` 和 prompt 名称规范化逻辑；
- 防止 prompt loader 通过路径分隔符读取任意文件；
- 新增 `tests/test_llm_runtime_prompts.py`；
- 更新 README、AGENTS、系统设计、技术路线、LLM 运行逻辑和 Phase 4 计划文档；
- 将当前版本更新为 `v4.2.0 Phase 4 Prompt And Policy Files`。

## v4.1.0 - Phase 4 LLM Provider Interface

在 `v4.0.0` LLM Runtime Contracts 基础上继续推进 Phase 4，定义叙事 provider 接口，但仍不接真实模型。

已完成：

- 新增 `llm_runtime/providers.py`；
- 新增 `NarrationProvider` 基类接口；
- 新增 `TemplateNarrationProvider`，用于本地确定性运行；
- 新增 `OpenAINarrationProvider` 占位类，明确真实 OpenAI 调用尚未实现；
- `render_safe_narration()` 支持通过 provider 获取 `NarrationProposal`；
- 保留旧的函数式 `proposer` 参数，兼容 v4.0 测试和调用方式；
- 新增 `tests/test_llm_runtime_providers.py`；
- 更新 README、AGENTS、系统设计、技术路线和 LLM 运行逻辑文档；
- 将当前版本更新为 `v4.1.0 Phase 4 LLM Provider Interface`。

## v4.0.0 - Phase 4 LLM Runtime Contracts

在 `v3.1.0` Persistence Complete 基础上进入 Phase 4，先建立 LLM 运行时的结构化提案契约，不接真实模型。

已完成：

- 新增 `docs/phase4_llm_runtime_plan.md`，梳理 Phase 4 的完整开发清单；
- 新增 `llm_runtime/`；
- 新增 `llm_runtime/contracts.py`；
- 新增 `NarrationProposal`、`NarrationValidation`、`NarrationResult`；
- 新增 `llm_runtime/narrator.py`；
- 实现叙事提案验证：只能 claim `rule_result` 已授权的状态变化、线索和地点；
- 实现安全回退：非法提案自动回退到确定性规则文本；
- 新增 `tests/test_llm_runtime_narrator.py`；
- 小重构：把 CLI 角色创建交互从 `character.py` 移到 `main.py`，让 `character.py` 保持模型/构造职责；
- 更新 README、AGENTS、系统设计、LLM 运行逻辑设计和技术路线文档；
- 将当前版本更新为 `v4.0.0 Phase 4 LLM Runtime Contracts`。

## v3.1.0 - Phase 3 Persistence Complete

在 `v3.0.0` SQLite baseline 基础上完成 Phase 3 持久化收尾，让 API 存储层更接近真实后端服务。

已完成：

- 新增 `phase3_persistence/config.py`，支持通过 `PANTHEON_DB_PATH` 配置 SQLite 数据库路径；
- 新增 `phase3_persistence/errors.py`，统一持久化层异常；
- `game_sessions.state_json` 改为版本化 snapshot envelope：`snapshot_version + state`；
- repository 兼容读取旧版未包裹的 `GameState` JSON；
- 新增 `game_events` 表，用 `game_id + event_index` 保存有序事件日志；
- 新增 `GET /games/{game_id}/events`，读取某局游戏的事件日志；
- `session_store.py` 将持久化异常统一转换为 API 500 错误；
- 补充 SQLite repository 测试：环境变量路径、版本化 snapshot、事件日志、坏 JSON；
- 补充 API 测试：事件日志读取、空事件、缺失游戏事件查询；
- 更新 README、AGENTS、系统设计、Phase 2 API 计划和技术路线文档；
- 将当前版本更新为 `v3.1.0 Phase 3 Persistence Complete`。

## v3.0.0 - Phase 3 Persistence Baseline

在 `v2.1.0` FastAPI Complete 基础上进入 Phase 3，把 API 游戏会话从进程内存升级为 SQLite 持久化。

已完成：

- 新增 `phase3_persistence/`；
- 新增 `phase3_persistence/sqlite_repository.py`；
- 使用 Python 标准库 `sqlite3` 保存 `game_id -> GameState JSON snapshot`；
- `POST /games` 创建游戏后写入 SQLite；
- `POST /games/{game_id}/actions` 执行动作后保存最新游戏状态；
- `GET /games`、`GET /games/{game_id}` 和 `DELETE /games/{game_id}` 改为通过 repository 访问持久化会话；
- 保持 Phase 2 API 路由形状不变；
- 新增 `tests/test_sqlite_repository.py`；
- API 测试改为使用临时 SQLite 数据库；
- `.gitignore` 忽略本地数据库文件 `data/*.sqlite3` 和 `data/*.db`；
- 更新 README、AGENTS、系统设计和技术路线文档。

## v2.1.0 - Phase 2 Complete

在 `v2.0.0` FastAPI baseline 上补齐 Phase 2 进入 Phase 3 前需要的配置查询、基础会话管理、schema 打磨、测试和系统设计文档。

已完成：

- 新增 `GET /games`：列出当前内存中的游戏会话摘要；
- 新增 `DELETE /games/{game_id}`：删除指定内存游戏会话；
- 新增 `GET /gods`：返回固定神明列表，方便未来前端创建角色；
- 为 `health`、`classes`、`gods`、`locations` 等只读接口补充 response model；
- 新增 `GameSessionSummary`、`GameListResponse`、`GameDeleteResponse`；
- 扩展 `session_store.py`，支持会话摘要、会话列表和会话删除；
- 扩展 `tests/test_phase2_api.py`，覆盖神明列表、游戏列表、删除成功、删除不存在游戏、空行动文本、OpenAPI schema；
- 新增 `docs/system_design.md`，记录 Phase 1、Phase 2、Phase 3 的系统设计、模块职责和数据流；
- 更新 `README.md`、`AGENTS.md`、`docs/phase2_api_plan.md`、`docs/technical_roadmap.md`；
- 将当前版本更新为 `v2.1.0 Phase 2 Complete`。
- 将职业显示名从 `猎人 / Hunter` 调整为 `游侠 / Ranger`，内部 `class_id` 暂时保持 `hunter` 以兼容旧数据。
- 将 `圣律之神` 调整为 `审判之神`，并补充八大神明的典籍神名。
- 将伊斯特亚政体设定为商人寡头君主制。
- 扩展五大列强设定，并新增控制 `金门海峡` 的 `塞勒米亚苏丹国`。
- 扩展八大神明和六大职业的详细设定，包括教会、禁忌、祝福、诅咒、职业定位、优势场景和玩法机制倾向。
- 新增五大列强前三核心城市设定，并补充塞勒米亚、罗斯维亚等其他重要国家首都。

## v2.0.0 - Phase 2 FastAPI Baseline

在 `v1.4.0` API Readiness 结构上正式进入 Phase 2，把 Phase 1 CLI 核心能力暴露成最小 FastAPI 服务。

已完成：

- 新增 `phase2_api/`；
- 新增 FastAPI app 入口 `phase2_api/main.py`；
- 新增 Pydantic schemas；
- 新增 route modules：
  - `GET /health`
  - `GET /classes`
  - `GET /locations`
  - `POST /characters`
  - `POST /games`
  - `GET /games/{game_id}`
  - `POST /games/{game_id}/actions`
- 新增内存会话存储 `phase2_api/services/session_store.py`；
- API 通过 `phase1_cli.game_service.handle_player_input()` 复用 Phase 1 游戏核心；
- 新增 `tests/test_phase2_api.py`；
- 新增 FastAPI / Uvicorn / HTTPX 依赖；
- 更新 README 的运行方式、API 接口说明和 Phase 2 状态。

## v1.4.0 - Phase 1 CLI API Readiness

在 `v1.3.0` 导航辅助版本上做 Phase 2 前置整理，让当前 CLI 逻辑更容易迁移到 FastAPI。

已完成：

- 新增 `game_service.py`；
- 新增 `phase1_cli/__init__.py`，让 Phase 1 代码成为可导入 Python package；
- 把系统命令和玩家行动处理从 `main.py` 抽到 `handle_player_input()`；
- 新增 `GameResponse`，统一表达行动结果、系统命令、存档/读档信号和退出信号；
- 新增 `GameResponse.to_dict()`，为未来 API response 准备结构；
- 新增 `Character.to_public_dict()`；
- 新增 `GameState.to_public_dict()`；
- 新增 `docs/phase2_api_plan.md`；
- 新增 `tests/test_game_service.py`；
- 测试改为通过 `phase1_cli.xxx` 包路径导入模块；
- 更新 README 的项目结构、文件职责和 Phase 2 说明。

## v1.3.0 - Phase 1 CLI Navigation Polish

在 `v1.2.0` Demo 展示版本上继续打磨导航和回顾体验，让玩家更清楚自己在哪里、去过哪里、最近发生过什么。

已完成：

- 新增 `地图 / map` 命令；
- 新增 `日志 / log / history` 命令；
- `地图` 会显示当前位置、已到达地点、未探索地点和当前位置出口；
- `日志` 会显示最近行动事件，默认展示最近 5 条；
- 更新 `HELP_TEXT`，补充地图和日志命令；
- 更新 README 的版本状态、命令说明、项目结构和当前限制；
- 扩展 `tests/test_story_views.py`；
- 自动化测试覆盖地图和行动日志展示逻辑。

## v1.2.0 - Phase 1 CLI Demo Polish

在 `v1.1.0` 存档/读档版本上继续打磨 CLI 展示体验，让项目更适合试玩、演示和面试讲解。

已完成：

- 新增 `目标 / goal / objective` 命令；
- 新增 `线索 / clues / clue` 命令；
- `目标` 会显示主线目标、核心线索进度和危险阈值；
- `线索` 会显示已发现线索，并标记普通线索和核心线索；
- 更新 `HELP_TEXT`，补充查看类命令；
- 更新 README，加入普通逃离路线和揭露真相路线；
- 新增 `tests/test_story_views.py`；
- 自动化测试覆盖目标和线索展示逻辑。

## v1.1.0 - Phase 1 CLI Save/Load

在 `v1.0.0` CLI baseline 上继续打磨，重点解决“游戏状态只在内存中，退出后丢失”的问题，并补上最小自动化测试。

已完成：

- 新增 `save_manager.py`；
- 支持本地 JSON 存档：游戏中输入 `存档`；
- 支持本地 JSON 读档：游戏中输入 `读档`；
- 启动时检测到本地存档可选择读取；
- `Character` 和 `GameState` 支持 `from_dict()`；
- 存档会保存职业规则修正、线索、背包、当前位置、回合数、访问地点和事件日志；
- 新增 `tests/test_intent_parser.py`；
- 新增 `tests/test_save_manager.py`；
- 使用 Python 标准库 `unittest`，不引入第三方测试依赖；
- 更新 README 的运行、测试、存档说明。

## v1.0.0 - Phase 1 CLI Baseline

项目正式命名为「神座纪元 / Pantheon Age」。

说明：`Phase 1` 命令行版本作为项目正式公开起点 `v1.0.0` 记录。

已完成：

- Python 标准库命令行文字冒险；
- 角色创建、职业系统、神明选择；
- 雾中修道院小副本；
- 关键词意图识别；
- d20 Rule Engine；
- HP / SAN / Suspicion / Corruption 状态管理；
- 地点移动、调查、分析、攻击、祈祷、休息、潜行、道具使用；
- 逐步线索获得；
- 普通逃离、揭露真相、深渊污染等结局；
- 修正“前往祈祷大厅”误判为祈祷的问题；
- 终端行动结果分隔和基础颜色提示；
- README 与 CHANGELOG 初版。
