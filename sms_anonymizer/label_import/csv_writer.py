import csv

from ..schema.labels import LABEL_TO_INT


def write_final_csv(rows: list[tuple[str, str, str]], output_path: str) -> None:
    """rows: (id, text, label) — id is dropped, output matches the model's
    expected text,label schema (label=1 scam, label=0 ham)."""
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "label"])
        for _row_id, text, label in rows:
            writer.writerow([text, LABEL_TO_INT[label]])
