import hashlib
import json
from datetime import datetime, timezone

from ..anonymize.rules import RULES_VERSION
from .versioning import next_corpus_version


def hash_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_manifest(
    output_file_path: str,
    manifest_path: str,
    version_state_path: str,
    counts_by_source: dict,
    discards_by_reason: dict,
    replacement_counts: dict,
) -> dict:
    output_hash = hash_file(output_file_path)
    corpus_version = next_corpus_version(version_state_path, output_hash)

    manifest = {
        "corpus_version": corpus_version,
        "rules_version": RULES_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "output_file_sha256": output_hash,
        "counts_by_source": counts_by_source,
        "discards_by_reason": discards_by_reason,
        "replacement_counts": replacement_counts,
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    return manifest
