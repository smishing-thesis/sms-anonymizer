from collections import Counter

from ..pipeline.records import ProcessedMessage


def sender_distribution(messages: list[ProcessedMessage]) -> dict:
    """Distribution by pseudonymous sender id, to catch a single sender
    dominating the corpus. Falls back to 'unknown' when no sender was captured."""
    counts = Counter(m.sender_pseudo_id or "unknown" for m in messages)
    total = len(messages)
    return {
        sender_id: {"count": count, "share": round(count / total, 4) if total else 0.0}
        for sender_id, count in counts.most_common()
    }
