import json
from dataclasses import asdict

from .rules import RULES_VERSION, SENDER_CATEGORIES, TEXT_RULES


def build_spec() -> dict:
    """Contract document for the thesis appendix and the future Kotlin
    reimplementation: same rules, same placeholders, same version."""
    return {
        "rules_version": RULES_VERSION,
        "text_rules": [asdict(rule) for rule in TEXT_RULES],
        "sender_categories": SENDER_CATEGORIES,
    }


def write_spec(output_path: str) -> None:
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(build_spec(), f, ensure_ascii=False, indent=2)
