"""Context packing for Agentic Runtime LLM providers.

This module is the small, local precursor to full RAG. It builds a compact turn
context instead of dumping every document into every LLM call.
"""

from functools import lru_cache
import os
from pathlib import Path
import re

from phase1_cli.scenarios import current_scene_focus_for_state
from rag.canon import retrieve_canon_chunks


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAG_SEED_PATH = PROJECT_ROOT / "docs" / "rag_seed_cards.md"
MAX_CARD_CHARS = 900
CANON_RETRIEVAL_ENV_VAR = "PANTHEON_CANON_RETRIEVAL"
DEFAULT_CANON_RETRIEVAL_STRATEGY = "keyword"


def build_context_pack(
    state,
    user_text="",
    memory_retrieval=None,
    open_action=None,
    temporary_content=(),
    adjudication=None,
    commit=None,
    lore_card_limit=6,
):
    """Return compact, relevant context for creative LLM agents."""
    query = build_query_text(state, user_text, open_action, adjudication, commit)
    return {
        "purpose": "Give LLM enough relevant context to imagine scenes without dumping the full canon.",
        "player": build_player_context(state),
        "location": build_location_context(state, memory_retrieval),
        "action": open_action.to_dict() if open_action else {"raw_text": user_text},
        "adjudication": adjudication.to_dict() if adjudication else {},
        "commit": commit.to_dict() if commit else {},
        "validated_scene_context": [content.to_dict() for content in temporary_content],
        "visible_memory": build_visible_memory(memory_retrieval),
        "recent_events": list(memory_retrieval.recent_events) if memory_retrieval else [],
        "relevant_lore_cards": retrieve_relevant_lore_cards(query, limit=lore_card_limit),
        "generation_directives": build_generation_directives(),
    }


def build_player_context(state):
    player = state.player
    origin = player.flags
    return {
        "name": player.name,
        "class": player.class_name,
        "god": player.god,
        "stats": dict(player.stats),
        "hp": {"current": player.hp, "max": player.max_hp},
        "san": {"current": player.san, "max": player.max_san},
        "suspicion": player.suspicion,
        "corruption": player.corruption,
        "origin": {
            "country": origin.get("origin_country_formal_name"),
            "identity": origin.get("origin_identity"),
            "ethnicity": origin.get("origin_ethnicity"),
            "city": origin.get("origin_city"),
            "background": origin.get("background_name"),
            "church_context": origin.get("origin_church_context"),
        },
    }


def build_location_context(state, memory_retrieval):
    location_context = list(memory_retrieval.location_context) if memory_retrieval else []
    return {
        "current_location": state.current_location,
        "current_scene_focus": current_scene_focus_for_state(state),
        "location_continuity_rule": (
            "current_location is the city-level location. current_scene_focus is the concrete scene. "
            "If the player does not explicitly move, keep narration inside current_scene_focus. "
            "Nearby places may be mentioned as options, but do not narrate that the player went there."
        ),
        "location_context": location_context[:4],
    }


def build_visible_memory(memory_retrieval):
    if not memory_retrieval:
        return []
    visible = list(memory_retrieval.player_known) + list(memory_retrieval.location_context)
    return visible[-8:]


def build_generation_directives():
    return {
        "creative_rule": "LLM creates possibilities; code validates authority and commits truth.",
        "story_length": "For player-facing narration, prefer 4 to 8 short paragraphs when enough material exists.",
        "style": "Atmospheric tabletop GM prose in Chinese; no debug labels or system reports.",
        "authority": (
            "Do not grant clues, items, deaths, faction changes, permanent facts, upgrades, or endings "
            "unless commit.committed_effects explicitly allows them."
        ),
        "uncertainty": "Use rumors, pressure, hesitation, partial observations, and next hooks for unconfirmed content.",
    }


def build_query_text(state, user_text, open_action, adjudication, commit):
    parts = [
        user_text,
        state.current_location,
        current_scene_focus_for_state(state),
        state.player.class_name,
        state.player.god,
        state.player.flags.get("origin_country_formal_name", ""),
        state.player.flags.get("origin_city", ""),
        state.player.flags.get("background_name", ""),
    ]
    if open_action:
        parts.extend(
            [
                open_action.raw_text,
                open_action.primary_goal,
                open_action.method,
                " ".join(open_action.targets),
            ]
        )
    if adjudication:
        bridge = adjudication.bridge_action
        parts.extend(
            [
                str(bridge.get("risk_type", "")),
                str(bridge.get("target_profile", "")),
                " ".join(bridge.get("possible_blockers", []) or []),
            ]
        )
    if commit:
        parts.extend(commit.committed_effects)
    return " ".join(str(part) for part in parts if part)


def retrieve_relevant_lore_cards(query, limit=6):
    strategy = os.environ.get(CANON_RETRIEVAL_ENV_VAR, DEFAULT_CANON_RETRIEVAL_STRATEGY)
    try:
        canon_chunks = retrieve_canon_chunks(query, limit=limit, strategy=strategy)
    except Exception:
        canon_chunks = retrieve_canon_chunks(
            query,
            limit=limit,
            strategy=DEFAULT_CANON_RETRIEVAL_STRATEGY,
        )
    if canon_chunks:
        return [
            {
                "title": chunk["title"],
                "body": chunk["body"],
                "source_path": chunk["source_path"],
                "category": chunk["category"],
                "visibility": chunk["visibility"],
            }
            for chunk in canon_chunks
        ]

    cards = load_rag_seed_cards()
    scored = []
    query_terms = extract_query_terms(query)
    for card in cards:
        score = score_card(card, query_terms, query)
        if score > 0:
            scored.append((score, card))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [compact_card(card) for _, card in scored[:limit]]


@lru_cache(maxsize=1)
def load_rag_seed_cards():
    if not RAG_SEED_PATH.exists():
        return ()
    text = RAG_SEED_PATH.read_text(encoding="utf-8")
    chunks = re.split(r"\n(?=### )", text)
    cards = []
    for chunk in chunks:
        stripped = chunk.strip()
        if not stripped.startswith("### "):
            continue
        title, _, body = stripped.partition("\n")
        cards.append({"title": title.removeprefix("### ").strip(), "body": body.strip()})
    return tuple(cards)


def extract_query_terms(query):
    terms = set()
    for token in re.split(r"[\s，。、“”/|:：；;（）()\-]+", query):
        token = token.strip()
        if len(token) >= 2:
            terms.add(token)
    for keyword in (
        "海洋",
        "真理",
        "战争",
        "审判",
        "丰饶",
        "死亡",
        "隐秘",
        "深渊",
        "密仪会",
        "潮汐圣会",
        "白塔院",
        "铁血教团",
        "审判庭",
        "蔷薇圣庭",
        "安魂教团",
        "夜幕修会",
        "格兰威克",
        "卢塞恩",
        "格莱芬",
        "维伦纳",
        "阿尔卡萨",
        "诺克提亚",
        "萨莱姆",
        "维亚洛夫",
        "杀",
        "守卫",
        "巡逻",
        "教会",
        "港口",
        "码头",
    ):
        if keyword in query:
            terms.add(keyword)
    return terms


def score_card(card, query_terms, query):
    haystack = f"{card['title']}\n{card['body']}"
    score = 0
    for term in query_terms:
        if term and term in haystack:
            score += 3 if term in card["title"] else 1
    if card["title"] in query:
        score += 5
    return score


def compact_card(card):
    body = card["body"]
    if len(body) > MAX_CARD_CHARS:
        body = body[:MAX_CARD_CHARS].rstrip() + "\n[card truncated]"
    return {
        "title": card["title"],
        "body": body,
    }
