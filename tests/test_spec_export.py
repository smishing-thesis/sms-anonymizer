import json

from sms_anonymizer.anonymize.rules import RULES_VERSION
from sms_anonymizer.anonymize.spec_export import build_spec, write_spec


def test_build_spec_includes_version_and_all_text_rules():
    spec = build_spec()
    assert spec["rules_version"] == RULES_VERSION
    names = {rule["name"] for rule in spec["text_rules"]}
    assert names == {"url", "email", "phone_pe", "person_name"}


def test_write_spec_produces_valid_json(tmp_path):
    output = tmp_path / "spec.json"
    write_spec(str(output))

    with open(output, encoding="utf-8") as f:
        loaded = json.load(f)

    assert loaded["rules_version"] == RULES_VERSION
    assert "sender_categories" in loaded
