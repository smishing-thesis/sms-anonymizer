from sms_anonymizer.manifest.manifest_writer import write_manifest


def test_writes_manifest_with_expected_fields(tmp_path):
    output_file = tmp_path / "final.csv"
    output_file.write_text("text,label\nHola,ham\n", encoding="utf-8")

    manifest_path = str(tmp_path / "manifest.json")
    version_state_path = str(tmp_path / "version_state.json")

    manifest = write_manifest(
        output_file_path=str(output_file),
        manifest_path=manifest_path,
        version_state_path=version_state_path,
        counts_by_source={"android_xml": 10},
        discards_by_reason={"duplicate": 2},
        replacement_counts={"<PHONE_NUMBER>": 3},
    )

    assert manifest["corpus_version"] == "1.0.0"
    assert manifest["counts_by_source"] == {"android_xml": 10}
    assert manifest["discards_by_reason"] == {"duplicate": 2}
    assert manifest["replacement_counts"] == {"<PHONE_NUMBER>": 3}
    assert "rules_version" in manifest
    assert "output_file_sha256" in manifest
