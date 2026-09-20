from ..anonymize.ner_detector import find_names
from ..anonymize.regex_detectors import find_all as find_regex_spans


def scan_residuals(rows: list[tuple[str, str]]) -> list[dict]:
    """rows: (id, already-anonymized text) pairs. Re-runs every detector on
    the output — anything it still finds is a leak that slipped through."""
    findings = []
    for row_id, text in rows:
        spans = find_regex_spans(text) + find_names(text)
        if spans:
            findings.append(
                {
                    "id": row_id,
                    "count": len(spans),
                    "placeholders_missed": sorted({s.placeholder for s in spans}),
                }
            )
    return findings
