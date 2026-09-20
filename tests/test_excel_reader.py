import pytest
from openpyxl import Workbook

from sms_anonymizer.label_import.excel_reader import LabelValidationError, read_labeled_rows


def _write(path, rows):
    wb = Workbook()
    ws = wb.active
    ws.append(["id", "text", "label"])
    for row in rows:
        ws.append(list(row))
    wb.save(path)


def test_reads_fully_labeled_rows(tmp_path):
    path = tmp_path / "labeled.xlsx"
    _write(path, [("id:0", "Hola <NAMED_ENTITY>", "ham"), ("id:1", "Gana un premio ya", "scam")])

    rows = read_labeled_rows(str(path))

    assert rows == [("id:0", "Hola <NAMED_ENTITY>", "ham"), ("id:1", "Gana un premio ya", "scam")]


def test_raises_on_missing_label(tmp_path):
    path = tmp_path / "labeled.xlsx"
    _write(path, [("id:0", "Hola", None)])

    with pytest.raises(LabelValidationError, match="row 2"):
        read_labeled_rows(str(path))


def test_raises_on_invalid_label_value(tmp_path):
    path = tmp_path / "labeled.xlsx"
    _write(path, [("id:0", "Hola", "spam")])

    with pytest.raises(LabelValidationError, match="'spam'"):
        read_labeled_rows(str(path))


def test_skips_trailing_blank_rows(tmp_path):
    path = tmp_path / "labeled.xlsx"
    _write(path, [("id:0", "Hola", "ham"), (None, None, None)])

    rows = read_labeled_rows(str(path))

    assert len(rows) == 1
