from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RawMessage:
    id: str
    source: str
    direction: Optional[str]  # "in", "out", or None if the source doesn't tell us
    timestamp: Optional[int]  # raw value from the source, format varies by source
    body: str
    sender: Optional[str] = None  # raw address/handle — never leaves the process unanonymized
    service: Optional[str] = None  # e.g. "sms", "rcs", "imessage"
