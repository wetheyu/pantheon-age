"""Runtime play profiles for speed, cost, and debug defaults."""

from dataclasses import dataclass
import os


PLAY_PROFILE_ENV_VAR = "PANTHEON_PLAY_PROFILE"


@dataclass(frozen=True)
class RuntimeProfile:
    name: str
    label: str
    description: str
    env: dict[str, str]
    lore_card_limit: int
    runtime_notes_limit: int

    def to_dict(self):
        return {
            "name": self.name,
            "label": self.label,
            "description": self.description,
            "lore_card_limit": self.lore_card_limit,
            "runtime_notes_limit": self.runtime_notes_limit,
            "env": dict(self.env),
        }


RUNTIME_PROFILES = {
    "local": RuntimeProfile(
        name="local",
        label="Local Offline",
        description="零 API 成本的本地回退路径，用于自动化测试和离线调试。",
        lore_card_limit=2,
        runtime_notes_limit=1200,
        env={
            "PANTHEON_USE_LLM": "0",
            "PANTHEON_USE_AGENTIC_LLM": "0",
            "PANTHEON_CREATIVE_GM_MODE": "0",
            "PANTHEON_AGENTIC_TURN_DIRECTOR": "1",
            "PANTHEON_AGENTIC_FULL_LLM": "0",
            "PANTHEON_CANON_RETRIEVAL": "keyword",
            "PANTHEON_RAG_CHAR_LIMIT": "3000",
            "PANTHEON_OPENAI_MAX_OUTPUT_TOKENS": "1600",
            "PANTHEON_SHOW_RUNTIME": "0",
        },
    ),
    "fast": RuntimeProfile(
        name="fast",
        label="Fast Live Play",
        description="推荐真实试玩路径：一次 Creative GM 调用，本地验证、掷骰、记忆和提交。",
        lore_card_limit=3,
        runtime_notes_limit=1000,
        env={
            "PANTHEON_USE_LLM": "0",
            "PANTHEON_USE_AGENTIC_LLM": "1",
            "PANTHEON_CREATIVE_GM_MODE": "1",
            "PANTHEON_AGENTIC_TURN_DIRECTOR": "1",
            "PANTHEON_AGENTIC_FULL_LLM": "0",
            "PANTHEON_CANON_RETRIEVAL": "keyword",
            "PANTHEON_RAG_CHAR_LIMIT": "3600",
            "PANTHEON_OPENAI_MAX_OUTPUT_TOKENS": "2200",
            "PANTHEON_SHOW_RUNTIME": "0",
        },
    ),
    "quality": RuntimeProfile(
        name="quality",
        label="Quality Live Play",
        description="更高质量试玩路径：更多上下文和输出预算，适合关键演示前检查。",
        lore_card_limit=6,
        runtime_notes_limit=2200,
        env={
            "PANTHEON_USE_LLM": "0",
            "PANTHEON_USE_AGENTIC_LLM": "1",
            "PANTHEON_CREATIVE_GM_MODE": "1",
            "PANTHEON_AGENTIC_TURN_DIRECTOR": "1",
            "PANTHEON_AGENTIC_FULL_LLM": "0",
            "PANTHEON_CANON_RETRIEVAL": "vector_hybrid",
            "PANTHEON_RAG_CHAR_LIMIT": "9000",
            "PANTHEON_OPENAI_MAX_OUTPUT_TOKENS": "5000",
            "PANTHEON_SHOW_RUNTIME": "0",
        },
    ),
    "debug": RuntimeProfile(
        name="debug",
        label="Debug Live Play",
        description="调试路径：开启 runtime 输出，保留真实 LLM 单调用主线和较完整上下文。",
        lore_card_limit=5,
        runtime_notes_limit=2000,
        env={
            "PANTHEON_USE_LLM": "0",
            "PANTHEON_USE_AGENTIC_LLM": "1",
            "PANTHEON_CREATIVE_GM_MODE": "1",
            "PANTHEON_AGENTIC_TURN_DIRECTOR": "1",
            "PANTHEON_AGENTIC_FULL_LLM": "0",
            "PANTHEON_CANON_RETRIEVAL": "hybrid",
            "PANTHEON_RAG_CHAR_LIMIT": "7000",
            "PANTHEON_OPENAI_MAX_OUTPUT_TOKENS": "4000",
            "PANTHEON_SHOW_RUNTIME": "1",
        },
    ),
}


def active_runtime_profile(environ=None):
    environ = environ or os.environ
    raw_name = environ.get(PLAY_PROFILE_ENV_VAR, "").strip().lower()
    if not raw_name:
        return None
    return RUNTIME_PROFILES.get(raw_name)


def apply_runtime_profile(profile, environ=None):
    environ = environ or os.environ
    if profile is None:
        return None
    for key, value in profile.env.items():
        environ[key] = value
    environ[PLAY_PROFILE_ENV_VAR] = profile.name
    return profile


def available_runtime_profiles():
    return tuple(RUNTIME_PROFILES.values())
