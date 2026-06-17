from pathlib import Path

from openpyxl import Workbook
from sqlalchemy.orm import Session

from app.localization import COLUMN_LABELS, localized_value
from app.models import DuplicateDiscrepancy, Issue, ProcessingLog, RouteHistory, RouteRecord, StopRecord


def build_report(db: Session, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tables = {
        "Справочник маршрутов": _rows(db, RouteRecord),
        "Ошибки и предупреждения": _rows(db, Issue),
        "Дубли и расхождения": _rows(db, DuplicateDiscrepancy),
        "Остановки": _rows(db, StopRecord),
        "Журнал обработки": _rows(db, ProcessingLog),
        "История изменений": _rows(db, RouteHistory),
    }
    workbook = Workbook()
    default_sheet = workbook.active
    workbook.remove(default_sheet)
    for sheet_name, rows in tables.items():
        worksheet = workbook.create_sheet(title=sheet_name)
        if rows:
            headers = list(rows[0].keys())
            worksheet.append(headers)
            for row in rows:
                worksheet.append([row.get(header) for header in headers])
        else:
            worksheet.append(["Нет данных"])
        for column_cells in worksheet.columns:
            max_length = max(len(str(cell.value or "")) for cell in column_cells)
            worksheet.column_dimensions[column_cells[0].column_letter].width = min(max(max_length + 2, 12), 60)
    workbook.save(output_path)
    return output_path


def _rows(db: Session, model: type) -> list[dict]:
    rows = db.query(model).all()
    data = []
    for row in rows:
        item = {}
        for column in model.__table__.columns:
            value = getattr(row, column.name)
            item[COLUMN_LABELS.get(column.name, column.name)] = localized_value(value)
        data.append(item)
    return pd.DataFrame(data)
