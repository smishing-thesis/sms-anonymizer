from dataclasses import dataclass
from typing import Optional

# Bump this whenever a rule's pattern or placeholder changes — it gets
# stamped into every manifest and the exported spec file, and the Kotlin
# reimplementation must track the same value.
RULES_VERSION = "1.1.0"


@dataclass(frozen=True)
class Rule:
    name: str
    kind: str  # "regex" or "ner"
    placeholder: str
    priority: int  # higher wins when spans overlap
    pattern: Optional[str]
    description: str


# Single source of truth for text-body anonymization. Both the Python regex
# engine and the exported JSON spec (spec_export.py) read from this table —
# nothing about patterns/placeholders should live anywhere else.
TEXT_RULES: list[Rule] = [
    Rule(
        name="url",
        kind="regex",
        placeholder="<URL>",
        priority=2,
        # Matches scheme-based links AND bare domain+TLD (with or without a
        # path), since real smishing links rarely use http:// or www. —
        # e.g. "gobpost.sbs/osc", "cl4ro.pe/miclarocompras".
        pattern=r"https?://\S+|\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}(?:/\S*)?",
        description="Web links. Keeps the signal that a link existed without keeping its destination.",
    ),
    Rule(
        name="email",
        kind="regex",
        # Higher priority than "url": the bare-domain URL pattern can
        # otherwise match fragments on either side of the "@" and split an
        # email address into two unrelated <URL> spans.
        placeholder="<EMAIL_ADDRESS>",
        priority=3,
        pattern=r"[\w.+-]+@[\w-]+\.[\w.-]+",
        description="Email addresses.",
    ),
    Rule(
        name="phone_pe",
        kind="regex",
        placeholder="<PHONE_NUMBER>",
        priority=2,
        pattern=r"(?:\+?51[\s.-]?)?9\d{2}[\s.-]?\d{3}[\s.-]?\d{3}\b",
        description="Peruvian mobile phone numbers (9XXXXXXXX, optionally with +51).",
    ),
    Rule(
        name="person_name",
        kind="ner",
        placeholder="<NAMED_ENTITY>",
        priority=1,
        pattern=None,
        description="Person names, detected via spaCy es_core_news_lg NER (PER entities).",
    ),
]

# Sender (envelope) classification categories — not text placeholders, since
# the sender identity isn't part of the message body.
SENDER_CATEGORIES = ["short_code", "alphanumeric", "full_number", "unknown"]
