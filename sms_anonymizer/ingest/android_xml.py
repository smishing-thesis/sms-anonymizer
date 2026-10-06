import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterator

from .models import RawMessage

# SMS Backup & Restore convention: type=1 is received, type=2 is sent.
_DIRECTION_MAP = {"1": "in", "2": "out"}


def parse(path: str) -> Iterator[RawMessage]:
    root = ET.parse(path).getroot()
    stem = Path(path).stem  # keeps ids unique when several backups are ingested
    for index, elem in enumerate(root.findall("sms")):
        date = elem.get("date")
        yield RawMessage(
            id=f"android_xml:{stem}:{index}",
            source="android_xml",
            direction=_DIRECTION_MAP.get(elem.get("type")),
            timestamp=int(date) if date and date.isdigit() else None,
            body=elem.get("body") or "",
            sender=elem.get("address") or None,
            # SMS Backup & Restore's XML schema doesn't distinguish RCS from SMS
            service="sms",
        )
