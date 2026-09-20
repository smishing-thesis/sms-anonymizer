from collections import Counter

from .ner_detector import find_names
from .regex_detectors import find_all as find_regex_spans
from .spans import merge_spans


def anonymize(text: str) -> str:
    result, _ = anonymize_with_stats(text)
    return result


def anonymize_with_stats(text: str) -> tuple[str, Counter]:
    spans = merge_spans(find_regex_spans(text) + find_names(text))
    stats = Counter(span.placeholder for span in spans)
    if not spans:
        return text, stats

    parts = []
    cursor = 0
    for span in spans:
        parts.append(text[cursor : span.start])
        parts.append(span.placeholder)
        cursor = span.end
    parts.append(text[cursor:])
    return "".join(parts), stats
