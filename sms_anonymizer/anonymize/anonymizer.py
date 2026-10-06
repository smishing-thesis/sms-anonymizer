import re
from collections import Counter
from typing import Optional

from .known_names import find_known_names
from .ner_detector import find_names
from .regex_detectors import find_all as find_regex_spans
from .spans import merge_spans


def anonymize(text: str, known_names: Optional[re.Pattern] = None) -> str:
    result, _ = anonymize_with_stats(text, known_names)
    return result


def anonymize_with_stats(
    text: str, known_names: Optional[re.Pattern] = None
) -> tuple[str, Counter]:
    spans = merge_spans(
        find_regex_spans(text) + find_names(text) + find_known_names(text, known_names)
    )
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
