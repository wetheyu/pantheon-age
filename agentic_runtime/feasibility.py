"""World feasibility checks for obvious resource and authority gaps."""

MAJOR_PURCHASE_VERBS = (
    "买下",
    "购买",
    "购置",
    "收购",
    "置办",
    "入手",
    "拿下",
    "买",
)

MAJOR_ASSET_TERMS = (
    "庄园别墅",
    "庄园",
    "别墅",
    "豪宅",
    "宅邸",
    "房产",
    "地产",
    "大楼",
    "工厂",
    "矿山",
    "船队",
    "军舰",
    "飞艇",
    "银行",
    "铁路",
    "公司",
)

INQUIRY_OR_PREP_TERMS = (
    "打听",
    "询问",
    "问问",
    "了解",
    "调查",
    "估价",
    "看房",
    "参观",
    "谈谈",
    "商量",
    "贷款",
    "抵押",
    "融资",
    "寻找赞助",
    "找赞助",
    "找投资",
    "租",
)


def evaluate_world_feasibility(state, rule_action):
    """Return a compact decision for impossible one-step world actions.

    This layer does not forbid player imagination. It only says which outcomes
    cannot become reality in one turn because the character lacks money,
    authority, status, access, or legal permission.
    """
    text = " ".join(
        str(value or "")
        for value in (
            rule_action.get("raw_text"),
            rule_action.get("open_method"),
            rule_action.get("open_primary_goal"),
            " ".join(rule_action.get("open_requested_effects", ())),
        )
    )
    purchase = detect_major_purchase_request(text)
    if not purchase:
        return allowed_feasibility()

    wealth_level = int(state.player.flags.get("wealth_level") or 1)
    if wealth_level >= 4:
        return allowed_feasibility()

    asset = purchase["asset"]
    return {
        "blocked": True,
        "category": "resource_gap",
        "severity": "hard_gate",
        "asset": asset,
        "reason": (
            f"当前资源处境不足以直接买下{asset}。"
            "这类资产需要巨额现金、抵押物、合法身份、银行信用或赞助人。"
        ),
        "player_resource": {
            "wealth_level": wealth_level,
            "wealth_label": state.player.flags.get("wealth_label", "未知"),
            "resource_note": state.player.flags.get("resource_note", ""),
        },
        "suggested_paths": [
            f"打听{asset}的价格和所有者",
            "寻找愿意担保或投资的赞助人",
            "去银行、商会或贵族沙龙谈抵押与信用",
            f"先调查{asset}是否牵涉债务、继承纠纷或异常事件",
        ],
        "denied_effects": (
            "unconfirmed_purchase",
            "unconfirmed_property_acquisition",
            "insufficient_resources",
        ),
    }


def allowed_feasibility():
    return {
        "blocked": False,
        "category": "allowed",
        "severity": "none",
        "reason": "",
        "suggested_paths": [],
        "denied_effects": (),
    }


def detect_major_purchase_request(text):
    if not text:
        return None
    if contains_any(text, INQUIRY_OR_PREP_TERMS) and not contains_any(text, ("买下", "购买", "购置", "收购", "置办")):
        return None
    if not contains_any(text, MAJOR_PURCHASE_VERBS):
        return None
    asset = first_term(text, MAJOR_ASSET_TERMS)
    if not asset:
        return None
    return {"asset": asset}


def contains_any(text, terms):
    return any(term in text for term in terms)


def first_term(text, terms):
    for term in terms:
        if term in text:
            return term
    return ""
