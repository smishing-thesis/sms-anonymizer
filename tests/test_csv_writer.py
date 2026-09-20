import csv

from sms_anonymizer.label_import.csv_writer import write_final_csv


def test_writes_text_label_columns_with_int_labels(tmp_path):
    output = tmp_path / "final.csv"
    rows = [("id:0", "Hola <NAMED_ENTITY>", "ham"), ("id:1", "Gana un premio ya", "scam")]

    write_final_csv(rows, str(output))

    with open(output, newline="", encoding="utf-8") as f:
        reader = list(csv.reader(f))

    assert reader[0] == ["text", "label"]
    assert reader[1] == ["Hola <NAMED_ENTITY>", "0"]
    assert reader[2] == ["Gana un premio ya", "1"]
