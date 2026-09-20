import csv

import pytest

from sms_anonymizer.ingest.csv_source import parse


def _write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def test_reads_required_text_column_only(tmp_path):
    path = tmp_path / "aportes.csv"
    _write_csv(path, ["text"], [["Hola Juan Inventado"]])

    messages = list(parse(str(path)))

    assert len(messages) == 1
    assert messages[0].body == "Hola Juan Inventado"
    assert messages[0].sender is None
    assert messages[0].service is None


def test_reads_optional_columns_when_present(tmp_path):
    path = tmp_path / "aportes.csv"
    _write_csv(
        path,
        ["text", "sender", "timestamp", "service"],
        [["Oferta especial", "800000", "1700000000", "SMS"]],
    )

    messages = list(parse(str(path)))

    assert messages[0].sender == "800000"
    assert messages[0].timestamp == 1700000000
    assert messages[0].service == "sms"


def test_raises_when_text_column_missing(tmp_path):
    path = tmp_path / "aportes.csv"
    _write_csv(path, ["message"], [["Hola"]])

    with pytest.raises(ValueError, match="text"):
        list(parse(str(path)))
