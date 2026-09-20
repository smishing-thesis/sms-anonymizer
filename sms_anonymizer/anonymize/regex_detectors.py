import re

from .rules import TEXT_RULES
from .spans import Span

_COMPILED_BY_NAME = {
    rule.name: re.compile(rule.pattern, re.IGNORECASE) for rule in TEXT_RULES if rule.kind == "regex"
}
_RULE_BY_NAME = {rule.name: rule for rule in TEXT_RULES}


def _find_by_rule_name(text: str, rule_name: str) -> list[Span]:
    rule = _RULE_BY_NAME[rule_name]
    compiled = _COMPILED_BY_NAME[rule_name]
    return [Span(m.start(), m.end(), rule.placeholder, rule.priority) for m in compiled.finditer(text)]


def find_urls(text: str) -> list[Span]:
    return _find_by_rule_name(text, "url")


def find_emails(text: str) -> list[Span]:
    return _find_by_rule_name(text, "email")


def find_phones(text: str) -> list[Span]:
    return _find_by_rule_name(text, "phone_pe")


def find_all(text: str) -> list[Span]:
    return [span for name in _COMPILED_BY_NAME for span in _find_by_rule_name(text, name)]
