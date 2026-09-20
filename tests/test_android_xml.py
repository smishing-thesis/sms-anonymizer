from pathlib import Path

from sms_anonymizer.ingest.android_xml import parse

FIXTURE = Path(__file__).parent / "fixtures" / "sample_android.xml"


def test_parses_all_messages():
    messages = list(parse(str(FIXTURE)))
    assert len(messages) == 2


def test_maps_direction_and_body():
    messages = list(parse(str(FIXTURE)))
    assert messages[0].direction == "in"
    assert messages[1].direction == "out"
    assert "Rosa Ficticia" in messages[0].body


def test_assigns_stable_source_and_ids():
    messages = list(parse(str(FIXTURE)))
    assert messages[0].id == "android_xml:0"
    assert messages[0].source == "android_xml"


def test_captures_sender_and_service():
    messages = list(parse(str(FIXTURE)))
    assert messages[0].sender == "+51900000001"
    assert messages[0].service == "sms"
