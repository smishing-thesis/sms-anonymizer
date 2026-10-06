import sqlite3

from sms_anonymizer.ingest.ios_sms_db import parse


def _attributed_body(text: str) -> bytes:
    """Mimics the typedstream blob iOS stores when message.text is NULL."""
    raw = text.encode("utf-8")
    if len(raw) < 0x80:
        length = bytes([len(raw)])
    else:
        length = b"\x81" + len(raw).to_bytes(2, "little")
    header = (
        b"\x04\x0bstreamtyped\x81\xe8\x03\x84\x01@\x84\x84\x84\x12NSAttributedString\x00"
        b"\x84\x84\x08NSObject\x00\x85\x92\x84\x84\x84\x08NSString\x01\x95\x84\x01+"
    )
    return header + length + raw + b"\x86\x84\x02iI\x01"


def _make_fake_db(path):
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE handle (ROWID INTEGER PRIMARY KEY, id TEXT)")
    conn.execute(
        "CREATE TABLE message (ROWID INTEGER PRIMARY KEY, text TEXT, is_from_me INTEGER, "
        "date INTEGER, service TEXT, handle_id INTEGER, attributedBody BLOB)"
    )
    conn.execute("INSERT INTO handle (ROWID, id) VALUES (1, '+51900000111')")
    conn.executemany(
        "INSERT INTO message (text, is_from_me, date, service, handle_id, attributedBody) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        [
            ("Hola Juan Inventado, te llamo al 987000111", 0, 700000000, "SMS", 1, None),
            ("Todo bien, gracias", 1, 700000100, "iMessage", None, None),
            ("Mensaje RCS de prueba", 0, 700000200, "RCS", 1, None),
            (None, 0, 700000300, "SMS", 1, None),  # attachment-only message, no text
        ],
    )
    conn.commit()
    conn.close()


def test_skips_rows_without_any_text(tmp_path):
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


def test_recovers_text_from_attributed_body_when_text_is_null(tmp_path):
    db_path = tmp_path / "sample.db"
    _make_fake_db(str(db_path))
    long_text = "Aviso de entrega ñ " + "x" * 300  # forces the 2-byte length form
    conn = sqlite3.connect(str(db_path))
    conn.executemany(
        "INSERT INTO message (text, is_from_me, date, service, handle_id, attributedBody) "
        "VALUES (NULL, 0, 700000400, 'SMS', 1, ?)",
        [(_attributed_body("Paquete pendiente, firma requerida"),), (_attributed_body(long_text),)],
    )
    conn.commit()
    conn.close()

    bodies = [m.body for m in parse(str(db_path))]

    assert len(bodies) == 5
    assert "Paquete pendiente, firma requerida" in bodies
    assert long_text in bodies


def test_works_on_databases_without_attributed_body_column(tmp_path):
    db_path = tmp_path / "old.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE handle (ROWID INTEGER PRIMARY KEY, id TEXT)")
    conn.execute(
        "CREATE TABLE message (ROWID INTEGER PRIMARY KEY, text TEXT, is_from_me INTEGER, "
        "date INTEGER, service TEXT, handle_id INTEGER)"
    )
    conn.execute("INSERT INTO message (text, is_from_me, date, service) VALUES ('Hola', 0, 1, 'SMS')")
    conn.commit()
    conn.close()

    assert [m.body for m in parse(str(db_path))] == ["Hola"]


def test_ids_include_the_source_file_name(tmp_path):
    db_path = tmp_path / "sms-persona-ficticia.db"
    _make_fake_db(str(db_path))

    ids = [m.id for m in parse(str(db_path))]

    assert ids[0] == "ios_sms_db:sms-persona-ficticia:1"
