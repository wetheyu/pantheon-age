"""Provider interfaces and OpenAI-backed providers for Phase 4."""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, Field

from .actions import build_keyword_action_candidate
from .contracts import ActionCandidate, NarrationProposal
from .narrator import build_template_narration_proposal
from .prompts import load_prompt


DEFAULT_OPENAI_MODEL = "gpt5.5"
LLM_ENABLED_ENV_VAR = "PANTHEON_USE_LLM"
OPENAI_MODEL_ENV_VAR = "PANTHEON_OPENAI_MODEL"
OPENAI_PROVIDER_ENV_VAR = "PANTHEON_OPENAI_PROVIDER"
OPENAI_BASE_URL_ENV_VAR = "PANTHEON_OPENAI_BASE_URL"
RAG_CHAR_LIMIT_ENV_VAR = "PANTHEON_RAG_CHAR_LIMIT"
OPENAI_TIMEOUT_ENV_VAR = "PANTHEON_OPENAI_TIMEOUT"
OPENAI_MAX_OUTPUT_TOKENS_ENV_VAR = "PANTHEON_OPENAI_MAX_OUTPUT_TOKENS"
DEFAULT_OPENAI_PROVIDER = "openai"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"

ActionIntent = Literal[
    "move",
    "investigate",
    "analyze",
    "attack",
    "pray",
    "rest",
    "use_item",
    "stealth",
    "talk",
]
RiskTag = Literal[
    "combat",
    "corruption",
    "deception",
    "hp_loss",
    "noise",
    "resource",
    "san_loss",
    "social",
    "suspicion",
    "time",
    "travel",
    "unknown",
]
SkillTag = Literal[
    "attack",
    "analyze",
    "craft",
    "deceive",
    "force",
    "investigate",
    "lore",
    "medicine",
    "move",
    "perception",
    "pray",
    "ritual",
    "social",
    "stealth",
    "survival",
    "talk",
    "track",
    "travel",
    "use_item",
]


class OpenAIProviderError(RuntimeError):
    """Raised when an OpenAI provider cannot produce a valid proposal."""


class ActionCandidateOutput(BaseModel):
    intent: ActionIntent
    target: Optional[str] = None
    item: Optional[str] = None
    method: str = ""
    desired_outcome: str = ""
    risk_tags: list[RiskTag] = Field(default_factory=list)
    skill_tags: list[SkillTag] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    confidence: float = 0.75
    raw_text: str = ""
    source: str = "llm"


class NarrationOutput(BaseModel):
    text: str
    claimed_state_changes: list[str] = Field(default_factory=list)
    claimed_new_clues: list[str] = Field(default_factory=list)
    claimed_location_after: Optional[str] = None
    source: str = "llm"


@dataclass(frozen=True)
class RuntimeProviders:
    action_provider: "ActionCandidateProvider"
    narration_provider: "NarrationProvider"
    llm_enabled: bool
    model: Optional[str]
    reason: str
    provider_endpoint: Optional[dict] = None

    def to_dict(self):
        return {
            "action_provider": self.action_provider.provider_name,
            "narration_provider": self.narration_provider.provider_name,
            "llm_enabled": self.llm_enabled,
            "model": self.model,
            "endpoint": self.provider_endpoint if self.llm_enabled else None,
            "reason": self.reason,
        }


class ActionCandidateProvider:
    """Base interface for future action candidate providers."""

    provider_name = "base-action"

    def propose_action_candidate(self, user_text, current_location=""):
        raise NotImplementedError(
            "Action candidate providers must implement propose_action_candidate()."
        )


class KeywordActionCandidateProvider(ActionCandidateProvider):
    """Local provider that wraps the existing deterministic keyword parser."""

    provider_name = "keyword"

    def propose_action_candidate(self, user_text, current_location=""):
        return build_keyword_action_candidate(user_text, current_location)


class OpenAIActionCandidateProvider(ActionCandidateProvider):
    """OpenAI-backed action parser.

    The provider returns only an ActionCandidate. Validation and execution still
    happen in local Python code.
    """

    provider_name = "openai-action"

    def __init__(self, model=None, client=None, api_key=None):
        load_local_env()
        self.model = model or os.getenv(OPENAI_MODEL_ENV_VAR, DEFAULT_OPENAI_MODEL)
        self.client = client
        self.api_key = api_key

    def propose_action_candidate(self, user_text, current_location=""):
        payload = {
            "user_text": user_text,
            "current_location": current_location,
            "runtime_notes": load_runtime_notes(),
        }
        data = call_openai_structured(
            client=self.client,
            api_key=self.api_key,
            model=self.model,
            prompt_name="action_candidate",
            payload=payload,
            output_model=ActionCandidateOutput,
        )
        data.setdefault("raw_text", user_text)
        data["source"] = self.provider_name
        try:
            return ActionCandidate(**data)
        except TypeError as exc:
            raise OpenAIProviderError(f"OpenAI action candidate payload was invalid: {exc}") from exc


class NarrationProvider:
    """Base interface for future narration providers."""

    provider_name = "base"

    def propose_narration(self, game_response):
        raise NotImplementedError("Narration providers must implement propose_narration().")


class TemplateNarrationProvider(NarrationProvider):
    """Local provider that wraps deterministic story text as a safe proposal."""

    provider_name = "template"

    def propose_narration(self, game_response):
        return build_template_narration_proposal(game_response)


class OpenAINarrationProvider(NarrationProvider):
    """OpenAI-backed narration provider."""

    provider_name = "openai"

    def __init__(self, model=None, client=None, api_key=None):
        load_local_env()
        self.model = model or os.getenv(OPENAI_MODEL_ENV_VAR, DEFAULT_OPENAI_MODEL)
        self.client = client
        self.api_key = api_key

    def propose_narration(self, game_response):
        payload = {
            "player_action": game_response.action,
            "public_state": game_response.state.to_public_dict(),
            "rule_result": game_response.rule_result,
            "deterministic_text": game_response.text,
            "runtime_notes": load_runtime_notes(),
        }
        data = call_openai_structured(
            client=self.client,
            api_key=self.api_key,
            model=self.model,
            prompt_name="narrator",
            payload=payload,
            output_model=NarrationOutput,
        )
        data["source"] = self.provider_name
        try:
            return NarrationProposal(**data)
        except TypeError as exc:
            raise OpenAIProviderError(f"OpenAI narration payload was invalid: {exc}") from exc


def build_runtime_providers_from_env():
    """Build the providers used by the CLI/API service layer."""
    load_local_env()
    endpoint = openai_endpoint_summary()
    if not is_llm_enabled():
        return RuntimeProviders(
            action_provider=KeywordActionCandidateProvider(),
            narration_provider=TemplateNarrationProvider(),
            llm_enabled=False,
            model=None,
            reason=f"{LLM_ENABLED_ENV_VAR} is not enabled.",
            provider_endpoint=endpoint,
        )

    if not os.getenv("OPENAI_API_KEY"):
        return RuntimeProviders(
            action_provider=KeywordActionCandidateProvider(),
            narration_provider=TemplateNarrationProvider(),
            llm_enabled=False,
            model=None,
            reason="OPENAI_API_KEY is missing; using local fallback providers.",
            provider_endpoint=endpoint,
        )

    model = os.getenv(OPENAI_MODEL_ENV_VAR, DEFAULT_OPENAI_MODEL)
    return RuntimeProviders(
        action_provider=OpenAIActionCandidateProvider(model=model),
        narration_provider=OpenAINarrationProvider(model=model),
        llm_enabled=True,
        model=model,
        reason="OpenAI providers enabled.",
        provider_endpoint=endpoint,
    )


def is_llm_enabled():
    load_local_env()
    return os.getenv(LLM_ENABLED_ENV_VAR, "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def call_openai_structured(client, api_key, model, prompt_name, payload, output_model):
    """Call OpenAI Responses API and return a parsed dict."""
    openai_client = client or build_openai_client(api_key, timeout=get_openai_timeout())
    prompt = load_prompt(prompt_name)
    user_content = json.dumps(payload, ensure_ascii=False, indent=2)

    if client is None and get_openai_base_url():
        return call_openai_compatible_chat_structured(
            openai_client,
            model=model,
            prompt=prompt,
            user_content=user_content,
            output_model=output_model,
        )

    try:
        response = openai_client.responses.parse(
            model=model,
            instructions=prompt,
            input=user_content,
            text_format=output_model,
            max_output_tokens=get_openai_max_output_tokens(),
        )
    except Exception as exc:
        raise OpenAIProviderError(f"OpenAI provider call failed: {exc}") from exc

    return extract_structured_payload(response)


def call_openai_compatible_chat_structured(openai_client, model, prompt, user_content, output_model):
    """Call an OpenAI-compatible chat endpoint and validate JSON locally."""
    schema = json.dumps(output_model.model_json_schema(), ensure_ascii=False)
    system_content = (
        f"{prompt}\n\n"
        "Return only one valid JSON object. Do not wrap it in Markdown. "
        "The JSON must match this schema:\n"
        f"{schema}"
    )
    kwargs = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ],
        "max_tokens": get_openai_max_output_tokens(),
        "response_format": {"type": "json_object"},
    }

    try:
        response = openai_client.chat.completions.create(**kwargs)
    except Exception as first_exc:
        fallback_kwargs = dict(kwargs)
        fallback_kwargs.pop("response_format", None)
        try:
            response = openai_client.chat.completions.create(**fallback_kwargs)
        except Exception as second_exc:
            raise OpenAIProviderError(
                "OpenAI-compatible chat provider call failed: "
                f"json mode failed with {first_exc}; plain JSON retry failed with {second_exc}"
            ) from second_exc

    content = extract_chat_content(response)
    payload = parse_json_object(content)
    return validate_structured_payload(payload, output_model)


def extract_chat_content(response):
    choices = getattr(response, "choices", None)
    if not choices:
        raise OpenAIProviderError("OpenAI-compatible chat response did not contain choices.")
    message = getattr(choices[0], "message", None)
    content = getattr(message, "content", None) if message else None
    if not content:
        raise OpenAIProviderError("OpenAI-compatible chat response did not contain message content.")
    return content


def validate_structured_payload(payload, output_model):
    try:
        parsed = output_model(**payload)
    except Exception as exc:
        raise OpenAIProviderError(
            f"OpenAI-compatible chat response did not match {output_model.__name__}."
        ) from exc
    if hasattr(parsed, "model_dump"):
        return parsed.model_dump()
    return parsed.dict()


def build_openai_client(api_key=None, timeout=None, base_url=None):
    load_local_env()
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise OpenAIProviderError(
            "The openai package is not installed. Run: ./.venv/bin/python -m pip install -r requirements.txt"
        ) from exc

    configured_base_url = base_url if base_url is not None else get_openai_base_url()
    kwargs = {"timeout": timeout}
    if api_key:
        kwargs["api_key"] = api_key
    if configured_base_url:
        kwargs["base_url"] = configured_base_url
    return OpenAI(**kwargs)


def get_openai_base_url():
    load_local_env()
    value = os.getenv(OPENAI_BASE_URL_ENV_VAR, "").strip()
    return value or None


def get_openai_provider_label():
    load_local_env()
    value = os.getenv(OPENAI_PROVIDER_ENV_VAR, "").strip().lower()
    return value or DEFAULT_OPENAI_PROVIDER


def openai_endpoint_summary():
    """Return a safe provider summary without exposing keys or full request data."""
    base_url = get_openai_base_url()
    provider = get_openai_provider_label()
    if provider == DEFAULT_OPENAI_PROVIDER and base_url:
        provider = "openai_compatible"
    return {
        "provider": provider,
        "endpoint": "custom_openai_compatible" if base_url else "official_openai",
        "base_url_configured": bool(base_url),
        "base_url_origin": summarize_base_url_origin(base_url) if base_url else None,
    }


def summarize_base_url_origin(base_url):
    parsed = urlparse(base_url)
    if parsed.scheme and parsed.netloc:
        return f"{parsed.scheme}://{parsed.netloc}"
    return "custom"


def load_local_env(path=ENV_PATH):
    """Load local .env values without requiring an extra dependency.

    Existing environment variables win, so shell-provided secrets are not
    overwritten by the local file.
    """
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        parsed = parse_env_line(line)
        if parsed is None:
            continue
        key, value = parsed
        os.environ.setdefault(key, value)


def parse_env_line(line):
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None

    if stripped.startswith("export "):
        stripped = stripped[len("export ") :].strip()

    if "=" not in stripped:
        return None

    key, value = stripped.split("=", 1)
    key = key.strip()
    if not key:
        return None

    value = strip_env_value(value.strip())
    return key, value


def strip_env_value(value):
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def get_openai_timeout():
    raw_value = os.getenv(OPENAI_TIMEOUT_ENV_VAR, "30")
    try:
        timeout = float(raw_value)
    except ValueError:
        return 30.0
    return max(1.0, timeout)


def get_openai_max_output_tokens():
    raw_value = os.getenv(OPENAI_MAX_OUTPUT_TOKENS_ENV_VAR, "700")
    try:
        tokens = int(raw_value)
    except ValueError:
        return 700
    return max(64, tokens)


def extract_structured_payload(response):
    parsed = getattr(response, "output_parsed", None)
    if parsed is not None:
        if hasattr(parsed, "model_dump"):
            return parsed.model_dump()
        if isinstance(parsed, dict):
            return parsed

    output_text = getattr(response, "output_text", None)
    if output_text:
        return parse_json_object(output_text)

    raise OpenAIProviderError("OpenAI response did not contain structured output.")


def parse_json_object(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or start >= end:
            raise OpenAIProviderError("OpenAI response was not valid JSON.") from None
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError as exc:
            raise OpenAIProviderError("OpenAI response JSON could not be parsed.") from exc


def load_runtime_notes(limit=None):
    if limit is None:
        limit = int(os.getenv(RAG_CHAR_LIMIT_ENV_VAR, "6000"))
    note_files = (
        "docs/rag_seed_cards.md",
        "docs/tone_guide.md",
        "docs/forbidden_outputs.md",
        "docs/progression_design.md",
    )
    chunks = []
    for relative_path in note_files:
        path = PROJECT_ROOT / relative_path
        if path.exists():
            chunks.append(f"\n# {relative_path}\n{path.read_text(encoding='utf-8')}")

    notes = "\n".join(chunks)
    if len(notes) <= limit:
        return notes
    return notes[:limit] + "\n\n[Runtime notes truncated for prompt budget.]"
