import xml.etree.ElementTree as ET
from typing import Iterator

from .models import RawMessage

# SMS Backup & Restore convention: type=1 is received, type=2 is sent.
_DIRECTION_MAP = {"1": "in", "2": "out"}


def parse(path: str) -> Iterator[RawMessage]:
    root = ET.parse(path).getroot()
    for index, elem in enumerate(root.findall("sms")):
        date = elem.get("date")
        yield RawMessage(
            id=f"android_xml:{index}",
            source="android_xml",
            direction=_DIRECTION_MAP.get(elem.get("type")),
            timestamp=int(date) if date and date.isdigit() else None,
            body=elem.get("body") or "",
            sender=elem.get("address") or None,
            # SMS Backup & Restore's XML schema doesn't distinguish RCS from SMS
            service="sms",
        )
