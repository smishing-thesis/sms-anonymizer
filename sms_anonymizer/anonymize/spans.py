from dataclasses import dataclass


@dataclass(frozen=True)
class Span:
    start: int
    end: int
    placeholder: str
    priority: int = 0  # higher wins when spans overlap


def merge_spans(spans: list[Span]) -> list[Span]:
    # Process highest-priority spans first so they claim their range;
    # a lower-priority span that overlaps an already-claimed range is dropped.
    by_priority = sorted(spans, key=lambda s: (-s.priority, s.start))
    accepted: list[Span] = []
    for span in by_priority:
        if any(span.start < a.end and a.start < span.end for a in accepted):
            continue
        accepted.append(span)
    return sorted(accepted, key=lambda s: s.start)
