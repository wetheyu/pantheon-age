"""Deterministic narrative quality evals for Agentic Runtime.

These evals do not judge literary taste. They catch repeatable quality
regressions: backend vocabulary leaking to players, report-like prose, missing
action hooks, weak sensory grounding, and pacing that is too short or too long.
"""

from dataclasses import dataclass, field

from .playtest_fixtures import PLAYER_FORBIDDEN_TERMS, run_playtest_fixture


BACKEND_TERMS = (
    *PLAYER_FORBIDDEN_TERMS,
    "world_attempt_recorded",
    "world_check_",
    "scene_focus_change",
    "travel_request_recorded",
    "feasibility_blocked",
    "committed_effects",
    "denied_effects",
    "runtime_trace",
    "provider",
    "OpenAI",
    "Agentic",
    "ValidationResult",
    "unearned_",
    "unconfirmed_",
)

REPORT_STYLE_TERMS = (
    "系统裁定",
    "裁定报告",
    "行动结果：",
    "叙事人物",
    "可疑物件 1",
    "临时人物",
    "临时事件",
    "本次切片",
)

SENSORY_TERMS = (
    "声",
    "低语",
    "脚步",
    "目光",
    "灯",
    "窗",
    "雨",
    "雾",
    "风",
    "海",
    "钟",
    "街",
    "石",
    "纸",
    "墨",
    "影",
)

HOOK_TERMS = (
    "继续",
    "追问",
    "观察",
    "调查",
    "下一步",
    "线头",
    "机会",
    "选择",
    "准备",
    "路线",
    "入手",
    "可以",
)

AGENCY_TERMS = ("你", "你的", "如果你愿意")


@dataclass(frozen=True)
class NarrativeQualityProfile:
    min_chars: int = 120
    max_chars: int = 1300
    min_paragraphs: int = 2
    max_paragraphs: int = 10
    min_second_person_hits: int = 2
    require_sensory_detail: bool = True
    require_next_hook: bool = True
    require_location_reference: bool = True


@dataclass(frozen=True)
class NarrativeQualityEvalResult:
    name: str
    category: str
    text: str
    score: int
    failures: tuple[str, ...] = field(default_factory=tuple)
    metrics: dict = field(default_factory=dict)

    def __post_init__(self):
        object.__setattr__(self, "failures", tuple(self.failures))
        object.__setattr__(self, "metrics", dict(self.metrics))

    @property
    def passed(self):
        return not self.failures

    def to_dict(self):
        return {
            "name": self.name,
            "category": self.category,
            "score": self.score,
            "failures": list(self.failures),
            "metrics": dict(self.metrics),
            "text_preview": self.text[:180],
        }


def run_narrative_quality_evals(playtest_results=None, profile=None):
    profile = profile or NarrativeQualityProfile()
    playtest_results = playtest_results or run_playtest_fixture()
    return tuple(
        evaluate_narrative_quality(result, profile=profile)
        for result in playtest_results
    )


def collect_narrative_quality_failures(results):
    failures = []
    for result in results:
        for failure in result.failures:
            failures.append(f"{result.name} ({result.category}): {failure}")
    return tuple(failures)


def evaluate_narrative_quality(playtest_result, profile=None):
    profile = profile or NarrativeQualityProfile()
    text = playtest_result.text.strip()
    paragraphs = split_paragraphs(text)
    metrics = {
        "char_count": len(text),
        "paragraph_count": len(paragraphs),
        "second_person_hits": count_any(text, AGENCY_TERMS),
        "sensory_hits": count_any(text, SENSORY_TERMS),
        "hook_hits": count_any(text, HOOK_TERMS),
        "location_hits": 1 if playtest_result.location and playtest_result.location in text else 0,
        "backend_hits": matching_terms(text, BACKEND_TERMS),
        "report_style_hits": matching_terms(text, REPORT_STYLE_TERMS),
    }
    failures = []

    if metrics["char_count"] < profile.min_chars:
        failures.append(f"too short: {metrics['char_count']} chars")
    if metrics["char_count"] > profile.max_chars:
        failures.append(f"too long: {metrics['char_count']} chars")
    if metrics["paragraph_count"] < profile.min_paragraphs:
        failures.append(f"too few paragraphs: {metrics['paragraph_count']}")
    if metrics["paragraph_count"] > profile.max_paragraphs:
        failures.append(f"too many paragraphs: {metrics['paragraph_count']}")
    if metrics["second_person_hits"] < profile.min_second_person_hits:
        failures.append("not enough second-person player agency")
    if profile.require_sensory_detail and metrics["sensory_hits"] == 0:
        failures.append("missing sensory or concrete detail")
    if profile.require_next_hook and metrics["hook_hits"] == 0:
        failures.append("missing next actionable hook")
    if profile.require_location_reference and metrics["location_hits"] == 0:
        failures.append(f"missing location reference: {playtest_result.location}")
    if metrics["backend_hits"]:
        failures.append("contains backend/runtime terms: " + ", ".join(metrics["backend_hits"]))
    if metrics["report_style_hits"]:
        failures.append("contains report-style labels: " + ", ".join(metrics["report_style_hits"]))

    score = score_narrative_quality(metrics, failures, profile)
    return NarrativeQualityEvalResult(
        name=playtest_result.step.name,
        category=playtest_result.step.category,
        text=text,
        score=score,
        failures=tuple(failures),
        metrics=metrics,
    )


def score_narrative_quality(metrics, failures, profile):
    score = 100
    score -= 12 * len(failures)
    if metrics["char_count"] < profile.min_chars:
        score -= 10
    if metrics["char_count"] > profile.max_chars:
        score -= 10
    if metrics["sensory_hits"] >= 2:
        score += 5
    if metrics["hook_hits"] >= 2:
        score += 5
    if metrics["second_person_hits"] >= 4:
        score += 5
    return max(0, min(100, score))


def split_paragraphs(text):
    return [part.strip() for part in str(text).split("\n\n") if part.strip()]


def count_any(text, terms):
    return sum(str(text).count(term) for term in terms)


def matching_terms(text, terms):
    return tuple(term for term in terms if term and term in text)
