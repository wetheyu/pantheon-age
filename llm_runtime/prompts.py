"""Prompt loading helpers for LLM runtime modules."""

from pathlib import Path


PROMPT_ROOT = Path(__file__).resolve().parents[1] / "prompts"


class PromptNotFoundError(FileNotFoundError):
    """Raised when a requested prompt file does not exist."""


def normalize_prompt_name(prompt_name):
    if "/" in prompt_name or "\\" in prompt_name:
        raise ValueError("Prompt name must not contain path separators.")

    if prompt_name.endswith(".md"):
        return prompt_name
    return f"{prompt_name}.md"


def load_prompt(prompt_name, prompt_root=PROMPT_ROOT):
    prompt_file = prompt_root / normalize_prompt_name(prompt_name)
    if not prompt_file.exists():
        raise PromptNotFoundError(f"Prompt not found: {prompt_file}")
    return prompt_file.read_text(encoding="utf-8")


def list_prompt_names(prompt_root=PROMPT_ROOT):
    if not prompt_root.exists():
        return []
    return sorted(path.stem for path in prompt_root.glob("*.md"))
