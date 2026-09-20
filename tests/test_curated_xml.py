from pathlib import Path

from sms_anonymizer.ingest.curated_xml import parse

FIXTURE = Path(__file__).parent / "fixtures" / "sample_curated.xml"


def test_parses_all_messages():
    messages = list(parse(str(FIXTURE)))
    assert len(messages) == 2


def test_captures_sender_service_and_body():
    messages = list(parse(str(FIXTURE)))
    assert messages[0].sender == "+51 900 000 111"
    assert messages[0].service == "sms"
    assert messages[1].service == "imessage"
    assert "inventado" in messages[0].body


def test_assigns_id_from_message_attribute_and_marks_direction_in():
    messages = list(parse(str(FIXTURE)))
    assert messages[0].id == "curated_xml:fake_001"
    assert messages[0].direction == "in"


def test_parses_iso_timestamp_to_epoch_seconds():
    messages = list(parse(str(FIXTURE)))
    assert messages[0].timestamp == 1767279600
