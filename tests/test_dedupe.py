from sms_anonymizer.clean.dedupe import dedupe
from sms_anonymizer.pipeline.records import ProcessedMessage


def _msg(id_, text):
    return ProcessedMessage(
        id=id_,
        text=text,
        source="csv",
        service=None,
        sender_type="unknown",
        sender_pseudo_id=None,
        message_timestamp=None,
        processed_at="2026-01-01T00:00:00+00:00",
    )


def test_removes_exact_duplicates_case_insensitive():
    messages = [_msg("1", "Hola"), _msg("2", "hola"), _msg("3", "Chau")]

    kept, duplicate_count = dedupe(messages)

    assert [m.id for m in kept] == ["1", "3"]
    assert duplicate_count == 1


def test_no_duplicates_returns_all():
    messages = [_msg("1", "Hola"), _msg("2", "Chau")]

    kept, duplicate_count = dedupe(messages)

    assert len(kept) == 2
    assert duplicate_count == 0
