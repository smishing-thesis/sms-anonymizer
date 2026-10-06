import sqlite3
from pathlib import Path
from typing import Iterator, Optional

from .models import RawMessage

# Apple's "typedstream" serialization of an NSAttributedString: the plain text
# follows the NSString class marker, as a length-prefixed UTF-8 run.
_TEXT_MARKER = b"NSString"
_RUN_PREFIX = b"\x01+"


def _decode_attributed_body(blob: Optional[bytes]) -> Optional[str]:
    """Recover the message text from message.attributedBody.

    Since iOS 16 the Messages database often leaves message.text NULL and
    keeps the text only in this blob. Returns None if it can't be decoded.
    """
    if not blob:
        return None
    marker = blob.find(_TEXT_MARKER)
    if marker < 0:
        return None
    start = blob.find(_RUN_PREFIX, marker)
    if start < 0:
        return None
    pos = start + len(_RUN_PREFIX)
    if pos >= len(blob):
        return None
    # Length: one byte if < 0x80; 0x81 = 2-byte little-endian; 0x82 = 4-byte.
    first = blob[pos]
    if first == 0x81:
        length, pos = int.from_bytes(blob[pos + 1 : pos + 3], "little"), pos + 3
    elif first == 0x82:
        length, pos = int.from_bytes(blob[pos + 1 : pos + 5], "little"), pos + 5
    else:
        length, pos = first, pos + 1
    return blob[pos : pos + length].decode("utf-8", errors="replace") or None


def parse(path: str) -> Iterator[RawMessage]:
    stem = Path(path).stem  # keeps ids unique and traceable to the source file
    # mode=ro: never write to the user's original Messages database
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        has_attributed_body = any(
            row[1] == "attributedBody" for row in conn.execute("PRAGMA table_info(message)")
        )
        body_column = "message.attributedBody" if has_attributed_body else "NULL"
        cursor = conn.execute(
            f"""
            SELECT message.ROWID, message.text, {body_column}, message.is_from_me,
                   message.date, message.service, handle.id
            FROM message
            LEFT JOIN handle ON message.handle_id = handle.ROWID
            """
        )
        for rowid, text, attributed_body, is_from_me, date, service, sender in cursor:
            if text is None:
                text = _decode_attributed_body(attributed_body)
            if text is None:
                continue  # attachment-only message, no text anywhere
            yield RawMessage(
                id=f"ios_sms_db:{stem}:{rowid}",
                source="ios_sms_db",
                direction="out" if is_from_me else "in",
                timestamp=date,
                body=text,
                sender=sender,
                service=(service or "").lower() or None,
            )
    finally:
        conn.close()
