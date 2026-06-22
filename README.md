# 神座纪元 / Pantheon Age

**神座纪元（Pantheon Age）** 是一个以固定神明体系、异常副本、调查冒险和规则裁定为核心的文字冒险系统。当前 `Phase 1` 命令行版本作为项目正式起点发布为 `v1.0.0`。这个版本只使用 Python 标准库，不接 LLM、不接数据库、不做前端、不做 Docker，目标是先把「角色状态 + 意图识别 + 规则引擎 + 线索 + 结局」跑通。

核心原则：

```text
LLM 负责叙事，代码负责规则，数据库负责记忆，RAG 负责世界观一致性。
```

当前版本先由固定模板负责叙事，Rule Engine 负责所有会影响游戏结果的事情。

## 版本状态

```text
内部里程碑：Phase 1 CLI Baseline
对外起点版本：v1.0.0
下一公开版本：v1.1.0
```

`v1.0.0` 以 `Phase 1` 作为起点，已完成：

- 命令行连续游玩；
- 角色创建、职业、神明选择；
- 关键词意图识别；
- d20 属性检定；
- Rule Engine 状态裁定；
- HP / SAN / Suspicion / Corruption 管理；
- 道具、线索、地点移动；
- 三类主要结局；
- 终端颜色和行动结果分隔；
- 修正“前往祈祷大厅”误判为祈祷的问题；
- 初步 README 和 CHANGELOG 项目记录。

下一公开版本 `v1.1.0` 计划：

- 本地 JSON 存档 / 读档；
- 最小自动化测试；
- Demo 通关路线和 README 展示优化；
- 配置数据进一步整理，为 FastAPI 版本做准备。

## 项目结构

```text
project-root/
  phase1_cli/
    main.py
    character.py
    game_state.py
    intent_parser.py
    rule_engine.py
    story.py
    data.py
    utils.py
  CHANGELOG.md
  README.md
  requirements.txt
```

## 怎么运行

需要 Python 3.10+。

本机已创建好虚拟环境：

```bash
cd <project-root>
source .venv/bin/activate
python --version
```

当前虚拟环境版本：

```text
Python 3.12.13
```

`v1.0.0` 暂时只使用 Python 标准库，所以不需要安装第三方依赖。后续如果添加依赖，可以执行：

```bash
pip install -r requirements.txt
```

启动游戏：

```bash
cd <project-root>/phase1_cli
python main.py
```

启动后按提示创建角色、选择职业和信仰神明，然后输入自然语言行动。

## 支持的行动

示例：

```text
进入前厅
前往祈祷大厅
调查脚印
搜索档案柜
分析墙上的符文
攻击黑影
向死亡之神祈祷
悄悄撬开档案柜
使用止血药剂
喝下镇静药剂
休息一下
```

系统命令：

```text
帮助
状态
退出
```

## 文件职责

- `main.py`：程序入口，负责创建角色、启动循环、读取玩家输入、调用解析器和规则引擎。
- `character.py`：角色数据结构、职业选择、初始属性/HP/SAN/道具计算。
- `game_state.py`：保存当前回合、当前位置、是否结束、访问地点和事件日志。
- `intent_parser.py`：使用关键词把自然语言行动解析成标准 intent dict。
- `rule_engine.py`：当前版本的工程核心，负责 d20、属性检定、职业加成、战斗、状态变化、道具、线索和结局。
- `story.py`：根据规则结果输出固定剧情文本。未来可替换为 LLM 叙事层。
- `data.py`：项目名、版本号、职业、地图、地点描述、神明、道具、线索、关键词等配置。
- `utils.py`：通用小工具，例如安全输入、数值限制、编号选择、终端颜色。

## Rule Engine 控制了什么

Rule Engine 负责所有核心状态：

- HP 变化；
- SAN 变化；
- Suspicion 变化；
- Corruption 变化；
- d20 属性检定；
- 职业加成；
- 地点移动；
- 战斗结果；
- 道具消耗；
- 线索获得；
- 三个主要结局判断。

基础检定公式：

```text
d20 + 属性值 + 职业修正 >= DC
```

## 职业如何影响检定

职业通过三类配置影响规则：

- `stat_bonus`：改变初始力量、敏捷、智力、信仰。
- `hp_bonus` / `san_bonus`：改变初始 HP 和 SAN。
- `rule_modifiers`：给特定行动加成或惩罚。

例子：

- 战士攻击更强：`attack_bonus +2`。
- 法师分析神秘知识更强：`analyze_bonus +2`、`lore_bonus +2`，但接触禁忌知识 SAN 风险更高。
- 盗贼潜行和开锁更强，但隐秘路线会增加 Suspicion。
- 猎人追踪和侦察更强。
- 牧师祈祷、净化、抵抗污染更强。
- 炼金术士使用药剂、鉴定异常物质更强。

## 当前限制

- 意图识别是关键词规则，不是真正的自然语言理解。
- 剧情文本是固定模板，不接 LLM。
- 存档只在内存中，退出后不会保存。
- 地图只有「雾中修道院」一个小副本。
- 战斗和道具系统是最小可玩版本，还没有复杂怪物、装备或任务系统。

## 后续 Phase 2：改造成 FastAPI

完成 `v1.1.0` 工程打磨后，Phase 2 可以把当前 CLI 拆成 REST API：

- `POST /characters`：创建角色；
- `POST /games`：创建新游戏；
- `GET /games/{game_id}`：读取当前状态；
- `POST /games/{game_id}/actions`：提交玩家行动；
- `GET /classes`：查看职业配置；
- `GET /locations`：查看地图配置。

当前的模块拆分已经为 Phase 2 做准备：

- `intent_parser.py` 可以直接服务 API 请求；
- `rule_engine.py` 可以直接返回 JSON-like dict；
- `Character.to_dict()` 和 `GameState.to_dict()` 可以作为 Pydantic schema 的起点；
- `story.py` 未来可以替换成 LLM 调用层。

## 这个阶段学到什么

通过 `v1.0.0`，你会接触到：

- Python 文件拆分；
- dict/list/dataclass；
- 命令行输入输出；
- 游戏循环；
- 状态管理；
- 关键词意图识别；
- d20 随机检定；
- 配置化职业系统；
- 规则引擎与剧情文本解耦；
- 为 FastAPI、数据库和 LLM Agent Workflow 预留接口。
