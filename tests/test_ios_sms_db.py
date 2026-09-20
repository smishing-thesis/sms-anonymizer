import sqlite3

from sms_anonymizer.ingest.ios_sms_db import parse


def _make_fake_db(path):
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE handle (ROWID INTEGER PRIMARY KEY, id TEXT)")
    conn.execute(
        "CREATE TABLE message (ROWID INTEGER PRIMARY KEY, text TEXT, is_from_me INTEGER, "
        "date INTEGER, service TEXT, handle_id INTEGER)"
    )
    conn.execute("INSERT INTO handle (ROWID, id) VALUES (1, '+51900000111')")
    conn.executemany(
        "INSERT INTO message (text, is_from_me, date, service, handle_id) VALUES (?, ?, ?, ?, ?)",
        [
            ("Hola Juan Inventado, te llamo al 987000111", 0, 700000000, "SMS", 1),
            ("Todo bien, gracias", 1, 700000100, "iMessage", None),
            ("Mensaje RCS de prueba", 0, 700000200, "RCS", 1),
            (None, 0, 700000300, "SMS", 1),  # attachment-only message, no text
        ],
    )
    conn.commit()
    conn.close()


def test_skips_rows_with_null_text(tmp_path):
    db_path = tmp_path / "sample.db"
    _make_fake_db(str(db_path))

    messages = list(parse(str(db_path)))

    assert len(messages) == 3
    assert all(m.body is not None for m in messages)


def test_maps_direction_from_is_from_me(tmp_path):
    db_path = tmp_path / "sample.db"
    _make_fake_db(str(db_path))

    messages = list(parse(str(db_path)))

    assert messages[0].direction == "in"
    assert messages[1].direction == "out"
    assert messages[0].source == "ios_sms_db"


def test_includes_rcs_and_imessage(tmp_path):
    db_path = tmp_path / "sample.db"
    _make_fake_db(str(db_path))

    messages = list(parse(str(db_path)))

    services = {m.service for m in messages}
    assert services == {"sms", "imessage", "rcs"}
    assert messages[0].sender == "+51900000111"
