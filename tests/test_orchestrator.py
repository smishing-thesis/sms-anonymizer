import csv

from sms_anonymizer.anonymize import anonymizer
from sms_anonymizer.pipeline.orchestrator import run_ingest_and_anonymize


def _write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "sender"])
        writer.writerows(rows)


def test_full_run_anonymizes_cleans_and_dedupes(tmp_path, monkeypatch):
    monkeypatch.setattr(anonymizer, "find_names", lambda text: [])

    csv_path = tmp_path / "aportes.csv"
    _write_csv(
        csv_path,
        [
            ["Escribime al 987654321", "80800"],
            ["escribime al 987654321", "80800"],  # duplicate after anonymization
            ["ok", "BancoInventado"],  # below min length
            ["Un mensaje valido y distinto", "+51900000000"],
        ],
    )
    salt_path = str(tmp_path / ".sender_salt")

    messages, before_after, counts_by_source, discards, replacements = run_ingest_and_anonymize(
        [("csv", str(csv_path))], salt_path=salt_path, min_length=5
    )

    assert counts_by_source == {"csv": 4}
    assert discards["below_min_length"] == 1
    assert discards["duplicate"] == 1
    assert replacements["<PHONE_NUMBER>"] == 2
    assert len(messages) == 2
    assert len(before_after) == 4
    assert ("Escribime al 987654321", "Escribime al <PHONE_NUMBER>") in before_after

    kept_texts = {m.text for m in messages}
    assert "Escribime al <PHONE_NUMBER>" in kept_texts

    sender_types = {m.sender_type for m in messages}
    assert sender_types == {"short_code", "full_number"}
