from openpyxl import Workbook
from openpyxl.worksheet.datavalidation import DataValidation

from ..schema.labels import ALLOWED_LABELS


def write_labeling_workbook(rows: list[tuple[str, str]], output_path: str) -> None:
    """rows: (id, anonymized_text) pairs. Writes an id/text/label sheet with
    a dropdown restricting the label column to ALLOWED_LABELS."""
    wb = Workbook()
    ws = wb.active
    ws.title = "messages"
    ws.append(["id", "text", "label"])
    for row_id, text in rows:
        ws.append([row_id, text, None])

    last_row = max(len(rows) + 1, 2)
    dv = DataValidation(
        type="list",
        formula1=f'"{",".join(ALLOWED_LABELS)}"',
        allow_blank=True,
        showErrorMessage=True,
    )
    dv.error = f"Label must be one of: {', '.join(ALLOWED_LABELS)}"
    ws.add_data_validation(dv)
    dv.add(f"C2:C{last_row}")

    wb.save(output_path)
