---
id: canon.fact_authority
title: 世界事实分级
category: policy
visibility: public
tags: Canon Facts, Generated Facts, Temporary Flavor, 事实分级, 记忆, 提交, 验证
---

# 世界事实分级

## Canon Facts

Canon Facts 是开发者写死的核心设定。

包括世界时代背景、五大列强、塞勒米亚苏丹国、罗斯维亚大公国、核心城市、八大神明、六大职业、核心科技水平、核心世界规则、已确定主线真相、已确定历史事件、已存在的重要 NPC 和重要地点。

Canon Facts 不应由 LLM 临时生成或随意改写。

## Generated Facts

Generated Facts 是 LLM 生成后，通过校验并写入记忆的内容。

包括支线 NPC、地方秘社、小型异常事件、可重复访问地点、地区性传闻和可追踪委托。

Generated Facts 必须通过 validator 和 commit，不能仅靠叙事文本成立。

## Temporary Flavor

Temporary Flavor 只用于当前叙事氛围。

包括路人、酒馆老板、旅馆房间、码头搬运工、报纸小新闻、街头传闻、普通商店和一次性旅途事件。

Temporary Flavor 默认不进入长期记忆，也不改变世界现实。

## 程序职责

程序不应硬编码每一个 NPC、地点、道具、关系、团队和事件。程序的职责是定义权限、记忆、可见性、验证、提交和持久化边界，补足 LLM 容易上下文漂移、逻辑不统一、长期记忆差和过度确认玩家猜测的缺点。
