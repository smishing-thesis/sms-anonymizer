from sms_anonymizer.clean.length_filter import filter_min_length
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


def test_drops_messages_below_min_length():
    messages = [_msg("1", "Ok"), _msg("2", "Un mensaje mas largo")]

    kept, discarded = filter_min_length(messages, min_length=5)

    assert [m.id for m in kept] == ["2"]
    assert discarded == 1
