import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Iterator, Optional

from .models import RawMessage


def _parse_timestamp(date_iso: Optional[str]) -> Optional[int]:
    if not date_iso:
        return None
    try:
        return int(datetime.fromisoformat(date_iso).timestamp())
    except ValueError:
        return None


def parse(path: str) -> Iterator[RawMessage]:
    """Hand-curated <message> records (id, label, channel, sender_display,
    date_iso, body, ...), e.g. transcribed from screenshots. The existing
    <label> is intentionally ignored — every message still goes through
    manual scam/ham labeling like every other source."""
    root = ET.parse(path).getroot()
    for index, elem in enumerate(root.findall("message")):
        yield RawMessage(
            id=f"curated_xml:{elem.get('id') or index}",
            source="curated_xml",
            direction="in",
            timestamp=_parse_timestamp(elem.findtext("date_iso")),
            body=elem.findtext("body") or "",
            sender=elem.findtext("sender_display") or None,
            service=(elem.findtext("channel") or "").strip().lower() or None,
        )
