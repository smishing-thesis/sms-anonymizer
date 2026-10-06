import re
import unicodedata
from typing import Optional

from .rules import TEXT_RULES
from .spans import Span

_RULE = next(rule for rule in TEXT_RULES if rule.name == "known_names")
_MIN_NAME_LENGTH = 3  # shorter entries ("de", "la") would wreck ordinary text

# Accent-insensitive matching without changing string length (spans must stay
# aligned with the original text), so each vowel becomes a character class.
_ACCENT_CLASSES = {"a": "[aáàâä]", "e": "[eéèêë]", "i": "[iíìîï]", "o": "[oóòôö]", "u": "[uúùûü]"}


def _strip_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text) if not unicodedata.combining(c))


def _name_to_pattern(name: str) -> str:
    return "".join(
        _ACCENT_CLASSES.get(c, re.escape(c)) for c in _strip_accents(name).lower()
    )


def load_known_names(path: str) -> list[str]:
    """One name or surname per line; blank lines and '#' comments are ignored."""
    names = []
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            name = line.split("#", 1)[0].strip()
            if not name:
                continue
            if len(name) < _MIN_NAME_LENGTH:
                raise ValueError(
                    f"Known name {name!r} is shorter than {_MIN_NAME_LENGTH} characters; "
                    "it would match inside ordinary words."
                )
            names.append(name)
    return names


def compile_known_names(names: list[str]) -> Optional[re.Pattern]:
    """Whole-word, case- and accent-insensitive. Consecutive names separated by
    spaces collapse into one match, so "OLGA JACQUELINE VILLACREZ" is a single span."""
    unique = sorted({n.strip() for n in names if n.strip()}, key=len, reverse=True)
    if not unique:
        return None
    alternatives = "|".join(_name_to_pattern(n) for n in unique)
    return re.compile(
        rf"(?<!\w)(?:{alternatives})(?:[ \t]+(?:{alternatives}))*(?!\w)", re.IGNORECASE
    )


def find_known_names(text: str, pattern: Optional[re.Pattern]) -> list[Span]:
    if pattern is None:
        return []
    return [Span(m.start(), m.end(), _RULE.placeholder, _RULE.priority) for m in pattern.finditer(text)]
