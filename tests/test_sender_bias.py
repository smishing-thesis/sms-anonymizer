from sms_anonymizer.clean.sender_bias import sender_distribution
from sms_anonymizer.pipeline.records import ProcessedMessage


def _msg(id_, sender_pseudo_id):
    return ProcessedMessage(
        id=id_,
        text="texto",
        source="csv",
        service=None,
        sender_type="full_number",
        sender_pseudo_id=sender_pseudo_id,
        message_timestamp=None,
        processed_at="2026-01-01T00:00:00+00:00",
    )


def test_reports_share_per_sender():
    messages = [_msg("1", "SENDER_A"), _msg("2", "SENDER_A"), _msg("3", "SENDER_B")]

    distribution = sender_distribution(messages)

    assert distribution["SENDER_A"]["count"] == 2
    assert distribution["SENDER_A"]["share"] == 0.6667
    assert distribution["SENDER_B"]["count"] == 1


def test_groups_missing_sender_as_unknown():
    messages = [_msg("1", None)]
    distribution = sender_distribution(messages)
    assert distribution["unknown"]["count"] == 1
