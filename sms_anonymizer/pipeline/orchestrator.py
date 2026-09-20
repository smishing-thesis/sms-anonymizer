from collections import Counter
from datetime import datetime, timezone

from ..anonymize.anonymizer import anonymize_with_stats
from ..anonymize.sender import classify_sender, pseudonymize_sender
from ..clean.dedupe import dedupe
from ..clean.length_filter import filter_min_length
from ..clean.mojibake import fix_mojibake
from ..clean.normalize import normalize_whitespace
from ..ingest.registry import parse as ingest_parse
from .records import ProcessedMessage


def run_ingest_and_anonymize(
    sources: list[tuple[str, str]], salt_path: str, min_length: int
) -> tuple[list[ProcessedMessage], list[tuple[str, str]], dict, dict, dict]:
    """sources: (format_name, path) pairs. Returns (messages, before_after_pairs,
    counts_by_source, discards_by_reason, replacement_counts)."""
    processed: list[ProcessedMessage] = []
    before_after: list[tuple[str, str]] = []
    counts_by_source: Counter = Counter()
    discards_by_reason: Counter = Counter()
    replacement_counts: Counter = Counter()
    processed_at = datetime.now(timezone.utc).isoformat()

    for format_name, path in sources:
        for raw in ingest_parse(format_name, path):
            counts_by_source[format_name] += 1

            body = normalize_whitespace(fix_mojibake(raw.body))
            if not body:
                discards_by_reason["empty_after_cleaning"] += 1
                continue

            anonymized, stats = anonymize_with_stats(body)
            before_after.append((body, anonymized))
            replacement_counts.update(stats)

            processed.append(
                ProcessedMessage(
                    id=raw.id,
                    text=anonymized,
                    source=raw.source,
                    service=raw.service,
                    sender_type=classify_sender(raw.sender),
                    sender_pseudo_id=pseudonymize_sender(raw.sender, salt_path),
                    message_timestamp=raw.timestamp,
                    processed_at=processed_at,
                )
            )

    processed, too_short = filter_min_length(processed, min_length)
    discards_by_reason["below_min_length"] += too_short

    processed, duplicates = dedupe(processed)
    discards_by_reason["duplicate"] += duplicates

    return (
        processed,
        before_after,
        dict(counts_by_source),
        dict(discards_by_reason),
        dict(replacement_counts),
    )
