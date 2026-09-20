import csv
import random
from typing import Optional


def write_review_sample(
    pairs: list[tuple[str, str]], output_path: str, sample_size: int, seed: Optional[int] = None
) -> int:
    """pairs: (before, after) text pairs. Writes a random sample for manual
    review. Contains personal data — caller must write it under the
    gitignored data/ directory, never into the repo."""
    rng = random.Random(seed)
    sample = pairs if len(pairs) <= sample_size else rng.sample(pairs, sample_size)

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["before", "after"])
        writer.writerows(sample)

    return len(sample)
