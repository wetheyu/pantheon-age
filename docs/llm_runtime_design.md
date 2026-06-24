# Pantheon Age LLM Runtime Design

## 核心原则

`Pantheon Age` 需要尽可能利用 LLM 的创造力，但不能把世界现实完全交给 LLM。

原因：

- LLM 输出具有概率性；
- LLM 容易受上下文影响；
- LLM 容易迎合玩家当前说法；
- LLM 可能编造事实；
- LLM 可能破坏已存在设定。

因此项目采用以下原则：

```text
LLM 只能 propose。
系统负责 validate。
只有 validated content 才能 commit。
```

换句话说：

```text
LLM 输出不是事实。
玩家输入不是事实。
写入 GameState 的结构化结果才是事实。
```

## LLM 可以做什么

LLM 应该用于生成：

- 临时场景；
- 城市细节；
- 旅馆、酒馆、码头、工厂、教堂等地点；
- 普通 NPC；
- 支线委托；
- 报纸新闻；
- 街头传闻；
- 旅途事件；
- 对话内容；
- 氛围描写；
- 神秘异常表现；
- 调查过程中的细节；
- 无限流式的新鲜事件；
- 不同国家风格下的地方特色。

LLM 不是世界本身。

LLM 是世界内容的生成器。

真正的世界状态由系统保存。

## LLM 不能做什么

LLM 不能直接决定：

- 玩家 HP 变化；
- 玩家 SAN 变化；
- 玩家金钱变化；
- 玩家获得或失去物品；
- 玩家获得或失去线索；
- 玩家当前位置变化；
- 玩家死亡；
- NPC 死亡；
- 阵营关系变化；
- 国家关系变化；
- 世界重大历史变化；
- 神明设定变化；
- 主线任务阶段变化；
- 结局；
- 骰子判定结果；
- 数据库存储内容。

LLM 不能随意：

- 发明第九位神明；
- 发明第六大列强；
- 改变 19 世纪科技水平；
- 让角色使用明显超时代科技；
- 让玩家无代价旅行；
- 让 NPC 透露未解锁的核心秘密；
- 把临时生成内容直接变成永久设定；
- 因为玩家暗示某件事，就顺着玩家说法改写世界真相。

## 玩家输入不是事实

玩家输入只代表：

```text
玩家想做什么
```

或者：

```text
玩家认为可能是什么
```

它不代表世界真的如此。

例如玩家说：

```text
我觉得这个警探肯定是深渊教徒。
```

LLM 不能因为玩家这样说，就直接把警探设定成深渊教徒。

正确处理方式：

- LLM 可以生成警探紧张、回避、言辞模糊的表现。
- 规则系统根据真实隐藏状态决定警探到底是不是深渊教徒。
- 如果警探不是，LLM 不能为了迎合玩家猜测改变事实。
- 如果警探是，也要等玩家通过调查获得线索后逐步揭示。

## 区分玩家意图和世界事实

玩家说：

```text
我打开密室门，里面应该有一把神器。
```

系统应解析为：

```json
{
  "action_type": "open",
  "target": "secret_room_door",
  "player_assumption": "there may be an artifact inside"
}
```

而不是直接生成神器。

## 基本运行流程

```text
玩家输入
  ↓
Natural Language Parser / LLM Intent Parser
  ↓
结构化 Action
  ↓
game_service.py
  ↓
rule_engine.py
  ↓
状态变化 / 判定结果
  ↓
scene_generator.py / event_generator.py
  ↓
LLM 生成候选场景或叙事
  ↓
validator.py 校验
  ↓
memory_manager.py 决定是否写入记忆
  ↓
story.py / LLM Narrator 输出最终文本
  ↓
CLI / API / Web UI
```

## 结构化状态变化

所有重要变化必须写成结构化数据。

示例：

```json
{
  "hp_delta": 0,
  "san_delta": -1,
  "money_delta": -3,
  "location_changed": true,
  "new_location": "albion_fogport_station",
  "clues_added": ["ticket_with_salt_stain"],
  "items_added": [],
  "faction_changes": {
    "albion_police": -1
  }
}
```

不能只靠一段自然语言描述表示状态变化。

## 叙事必须服从状态

如果结构化结果里没有获得线索，叙事就不能写玩家发现了线索。

如果结构化结果里没有移动地点，叙事就不能写玩家已经到达别的城市。

如果结构化结果里没有 NPC 死亡，叙事就不能写 NPC 死了。

## RAG 的作用

RAG 是控制 LLM 输出的重要手段。

世界观不能全部塞进 prompt，也不能依赖 LLM 记忆。

未来可以把世界设定拆成多个可检索文档，例如：

```text
world_overview.md
countries/albion.md
countries/lumiere.md
countries/walde.md
countries/ost.md
countries/istea.md
gods/ocean.md
gods/truth.md
gods/war.md
gods/judgment.md
gods/abundance.md
gods/death.md
gods/secrecy.md
gods/abyss.md
classes/knight.md
classes/mage.md
classes/agent.md
classes/ranger.md
classes/priest.md
classes/alchemist.md
technology_level.md
tone_guide.md
forbidden_outputs.md
travel_rules.md
faction_rules.md
```

当玩家在某个国家、城市或事件中行动时，系统只检索相关文档给 LLM。

例如玩家在阿尔比昂港口调查海洋教会事件时，RAG 应检索：

- 阿尔比昂国家设定；
- 当前城市设定；
- 港口场景规则；
- 海洋之神设定；
- 海洋教会设定；
- 当前任务状态；
- 玩家已知线索；
- 技术水平限制；
- 禁止输出规则。

RAG 的作用不是让 LLM 完全可靠，而是减少它乱编的范围。

真正的可靠性还需要：

- 规则引擎；
- 状态管理；
- validator；
- memory manager。

## 内容分级

### Level 0：绝对固定设定

不能由 LLM 修改。

包括：

- 世界时代背景；
- 五大列强；
- 关键海峡国塞勒米亚苏丹国；
- 罗斯维亚大公国；
- 已设定核心城市；
- 八大神明；
- 六大职业；
- 核心科技水平；
- 核心世界规则；
- 已确定主线真相；
- 已确定历史事件；
- 已存在的重要 NPC；
- 已存在的重要地点。

### Level 1：固定设定的具体表现

LLM 可以根据 RAG 进行补充，但不能改变核心。

例如：

- 阿尔比昂首都的一个贫民区街道；
- 卢米埃某家咖啡馆；
- 瓦尔德某个铁路站；
- 奥斯特某个军官俱乐部；
- 伊斯特亚某个港口旅馆。

### Level 2：临时场景内容

LLM 可以自由度较高地生成。

例如：

- 路人；
- 酒馆老板；
- 旅馆房间；
- 码头搬运工；
- 报纸小新闻；
- 街头传闻；
- 普通商店；
- 一次性旅途事件。

这些内容默认是临时的。

除非系统决定保存，否则不会成为长期世界设定。

### Level 3：可持久化支线内容

LLM 可以生成，但必须经过 validator 和 memory manager 才能持久化。

例如：

- 一个支线 NPC；
- 一个地方秘社；
- 一个小型异常事件；
- 一个可重复访问的地点；
- 一个地区性传闻；
- 一个可追踪委托。

这些信息跟随存档。

每次开新档时，世界回到初始状态。

## 场景提案格式

LLM 生成场景时，应该输出结构化 proposal。

示例：

```json
{
  "scene_name": "灰鸥旅馆",
  "country": "阿尔比昂",
  "city": "雾港",
  "scene_type": "inn",
  "description": "一间靠近码头的廉价旅馆，空气里有煤烟、海盐和湿木头的气味。",
  "allowed_actions": ["rest", "ask_rumors", "rent_room", "inspect", "talk"],
  "npc_candidates": [
    {
      "name": "玛莎·克莱恩",
      "role": "旅馆老板",
      "attitude": "cautious",
      "secret_level": "minor"
    }
  ],
  "possible_clues": [
    {
      "clue_id": "rumor_missing_sailors",
      "visibility": "requires_conversation"
    }
  ],
  "risk_tags": ["pickpocket", "cult_rumor", "police_attention"],
  "deity_links": ["海洋之神", "隐秘之神"],
  "persistence": "temporary"
}
```

系统需要检查：

- 国家是否存在；
- 城市是否符合设定；
- 场景类型是否允许；
- 科技水平是否合理；
- 神明关联是否合理；
- NPC 是否过强；
- 是否泄露隐藏主线；
- 是否直接给玩家奖励；
- 是否改变世界大设定；
- 是否需要写入长期记忆。

通过校验后，场景才可以展示给玩家。

## 事件生成规则

事件也应由 LLM 提案，规则系统校验。

事件类型：

- 日常事件；
- 调查事件；
- 旅途事件；
- 神秘事件；
- 战斗事件；
- 社交事件；
- 阵营事件；
- 神明污染事件；
- 支线委托；
- 主线推进事件。

LLM 可以生成事件壳子。

例如：

```text
一名湿透的少年在火车站声称，
他从未登上过那艘已经沉没三十年的船，
但他的口袋里却有那艘船的船票。
```

但事件是否真的出现，需要系统判断：

- 当前地点是否合适；
- 当前神明污染值是否足够；
- 当前任务阶段是否允许；
- 玩家是否有相关线索；
- 随机事件概率是否触发；
- 事件等级是否过高；
- 事件奖励是否合理。

LLM 不能随便把所有场景都变成主线级大事件。

## LLM 调用类型

### Intent Parser

目标：把玩家自然语言变成结构化 action。

输入：

- 玩家输入；
- 当前地点；
- 可见对象；
- 可用动作列表。

输出示例：

```json
{
  "action_type": "inspect",
  "target": "corpse_ring",
  "method": "careful"
}
```

权限：

- 不能生成剧情；
- 不能修改状态；
- 不能决定结果。

### Scene Generator

目标：生成局部场景细节。

权限：

- 可以生成临时 NPC；
- 可以生成环境细节；
- 可以生成普通传闻；
- 不能生成重大世界变化。

### Event Generator

目标：生成可能发生的小事件或支线事件。

权限：

- 可以生成候选事件；
- 不能自动触发事件；
- 不能自动给奖励；
- 不能强行推进主线。

### Narrator

目标：把规则结果写成有氛围的文本。

输入：

- rule_result；
- visible_state；
- style guide。

权限：

- 不能改变 rule_result；
- 不能新增事实；
- 不能泄露隐藏信息。

### NPC Dialogue Generator

目标：生成 NPC 对话。

输入：

- NPC 设定；
- NPC 已知信息；
- NPC 对玩家态度；
- 当前场景；
- 玩家问题。

权限：

- 只能使用 NPC 知道的信息；
- 不能透露隐藏真相；
- 不能随意改变 NPC 立场。

### Memory Summarizer

目标：总结游戏历史。

权限：

- 只能总结已发生事实；
- 不能加入新事实；
- 不能直接写入数据库。

## 真实世界感的系统支撑

想让玩家感觉自己真实活在这个世界里，不能只靠 LLM 写得华丽。

还需要：

- 稳定世界规则；
- 持久化记忆；
- 时间推进；
- 地理约束；
- 社会身份约束；
- 信息边界。

## 防止上下文污染

不要把完整聊天记录直接当作事实来源。

每次调用 LLM 时，建议只提供：

- 当前玩家状态；
- 当前地点；
- 当前可见 NPC；
- 当前已发现线索；
- 当前任务阶段；
- RAG 检索到的相关设定；
- 本次玩家输入；
- 输出格式要求；
- 禁止事项。

这样可以减少 LLM 被长上下文带偏。

## 后续模块方向

未来可以逐步加入：

- `llm_intent_parser.py`
- `llm_scene_generator.py`
- `llm_event_generator.py`
- `llm_narrator.py`
- `validator.py`
- `memory_manager.py`
- `rag_retriever.py`

但这些都不应该在 Phase 2 最小 API 阶段一次性完成。

Phase 2 第一目标仍然是：

```text
把当前 CLI 能力稳定暴露成 FastAPI。
```
