import sqlite3
from typing import Iterator

from .models import RawMessage


def parse(path: str) -> Iterator[RawMessage]:
    # mode=ro: never write to the user's original Messages database
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        cursor = conn.execute(
            """
            SELECT message.ROWID, message.text, message.is_from_me, message.date,
                   message.service, handle.id
            FROM message
            LEFT JOIN handle ON message.handle_id = handle.ROWID
            WHERE message.text IS NOT NULL
            """
        )
        for rowid, text, is_from_me, date, service, sender in cursor:
            yield RawMessage(
                id=f"ios_sms_db:{rowid}",
                source="ios_sms_db",
                direction="out" if is_from_me else "in",
                timestamp=date,
                body=text,
                sender=sender,
                service=(service or "").lower() or None,
            )
    finally:
        conn.close()
