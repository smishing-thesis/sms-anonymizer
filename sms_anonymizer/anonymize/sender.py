import hashlib
import hmac
import os
import re
from typing import Optional

from .rules import SENDER_CATEGORIES

_DIGITS_ONLY_RE = re.compile(r"^\+?\d+$")
_SEPARATOR_RE = re.compile(r"[\s.-]")
SHORT_CODE_MAX_DIGITS = 6

assert set(SENDER_CATEGORIES) == {"short_code", "alphanumeric", "full_number", "unknown"}


def _normalize(sender: str) -> str:
    # Different sources format the same number differently ("+51 921 103 794"
    # vs "+51921103794") — strip formatting so classification and
    # pseudonymization are consistent regardless of source.
    return _SEPARATOR_RE.sub("", sender.strip())


def classify_sender(sender: Optional[str]) -> str:
    if not sender or not sender.strip():
        return "unknown"

    normalized = _normalize(sender)
    if _DIGITS_ONLY_RE.match(normalized):
        digits = normalized.lstrip("+")
        return "short_code" if len(digits) <= SHORT_CODE_MAX_DIGITS else "full_number"
    return "alphanumeric"


def _load_or_create_salt(salt_path: str) -> bytes:
    if os.path.exists(salt_path):
        with open(salt_path, "rb") as f:
            return f.read()

    salt = os.urandom(32)
    parent = os.path.dirname(salt_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(salt_path, "wb") as f:
        f.write(salt)
    return salt


def pseudonymize_sender(sender: Optional[str], salt_path: str) -> Optional[str]:
    """Deterministic pseudonymous id: same real sender always maps to the same
    id (needed for the concentration-by-sender report), but the id can't be
    reversed back to the phone number/handle without the local salt file."""
    if not sender or not sender.strip():
        return None

    salt = _load_or_create_salt(salt_path)
    digest = hmac.new(salt, _normalize(sender).encode("utf-8"), hashlib.sha256).hexdigest()
    return f"SENDER_{digest[:12]}"
