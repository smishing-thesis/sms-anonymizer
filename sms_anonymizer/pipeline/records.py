from dataclasses import dataclass
from typing import Optional


@dataclass
class ProcessedMessage:
    id: str
    text: str  # already anonymized and cleaned
    source: str
    service: Optional[str]
    sender_type: str  # one of anonymize.rules.SENDER_CATEGORIES
    sender_pseudo_id: Optional[str]
    message_timestamp: Optional[int]  # raw value from the source, not the message's actual date
    processed_at: str  # ISO 8601 UTC — when this pipeline run processed it
