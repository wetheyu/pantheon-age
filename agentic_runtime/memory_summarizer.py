"""Deterministic memory summaries for Phase 6.

The summarizer is extractive by design: it compresses committed memory records
without inventing new facts. LLM summarization can be added later behind the same
visibility boundaries.
"""


MAX_SUMMARY_ITEMS = 8
MAX_ENTRY_CHARS = 80
MAX_SUMMARY_CHARS = 520


def summarize_records_for_context(records, label, max_items=MAX_SUMMARY_ITEMS):
    """Return one compact summary string for committed memory records."""
    records = tuple(records)
    if not records:
        return ""

    selected = records[-max_items:]
    entries = []
    for record in selected:
        entries.append(f"{record.subject} -> {truncate(record.content, MAX_ENTRY_CHARS)}")

    prefix = f"{label}摘要（{len(records)}条早期记录"
    if len(records) > len(selected):
        prefix += f"，展示最近{len(selected)}条"
    prefix += "）："
    return truncate(prefix + "；".join(entries), MAX_SUMMARY_CHARS)


def summarize_and_format_records(records, label, recent_limit):
    """Return a bounded context list: one summary plus recent full records."""
    records = tuple(records)
    if len(records) <= recent_limit:
        return format_memory_records(records, label)

    older_records = records[:-recent_limit]
    recent_records = records[-recent_limit:]
    summary = summarize_records_for_context(older_records, label)
    formatted = [summary] if summary else []
    formatted.extend(format_memory_records(recent_records, label))
    return formatted


def format_memory_records(records, label):
    return [f"{label}：{record.subject} -> {record.content}" for record in records]


def truncate(text, limit):
    text = str(text)
    if len(text) <= limit:
        return text
    return text[: limit - 12].rstrip() + "...[truncated]"
