from ..pipeline.records import ProcessedMessage


def dedupe(messages: list[ProcessedMessage]) -> tuple[list[ProcessedMessage], int]:
    """Dedupe by normalized (case-folded, trimmed) text. Returns (kept, duplicate_count)."""
    seen = set()
    kept = []
    duplicate_count = 0
    for message in messages:
        key = message.text.strip().lower()
        if key in seen:
            duplicate_count += 1
            continue
        seen.add(key)
        kept.append(message)
    return kept, duplicate_count
