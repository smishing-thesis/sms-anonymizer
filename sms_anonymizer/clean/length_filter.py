from ..pipeline.records import ProcessedMessage


def filter_min_length(messages: list[ProcessedMessage], min_length: int) -> tuple[list[ProcessedMessage], int]:
    kept = [m for m in messages if len(m.text) >= min_length]
    return kept, len(messages) - len(kept)
