from ..anonymize.known_names import compile_known_names, find_known_names
from ..anonymize.ner_detector import find_names
from ..anonymize.regex_detectors import find_all as find_regex_spans


def scan_residuals(
    rows: list[tuple[str, str]], known_names: list[str] | None = None
) -> list[dict]:
    """rows: (id, already-anonymized text) pairs. Re-runs every detector on
    the output — anything it still finds is a leak that slipped through."""
    known_names_pattern = compile_known_names(known_names or [])
    findings = []
    for row_id, text in rows:
        spans = find_regex_spans(text) + find_names(text) + find_known_names(text, known_names_pattern)
        if spans:
            findings.append(
                {
                    "id": row_id,
                    "count": len(spans),
                    "placeholders_missed": sorted({s.placeholder for s in spans}),
                }
            )
    return findings
