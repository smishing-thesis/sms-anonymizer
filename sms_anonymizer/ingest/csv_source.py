import csv
from typing import Iterator

from .models import RawMessage


def parse(path: str) -> Iterator[RawMessage]:
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or "text" not in reader.fieldnames:
            raise ValueError("CSV source must have a 'text' column")

        for index, row in enumerate(reader):
            timestamp = (row.get("timestamp") or "").strip()
            yield RawMessage(
                id=f"csv:{index}",
                source="csv",
                direction=None,
                timestamp=int(timestamp) if timestamp.isdigit() else None,
                body=row.get("text") or "",
                sender=(row.get("sender") or "").strip() or None,
                service=(row.get("service") or "").strip().lower() or None,
            )
