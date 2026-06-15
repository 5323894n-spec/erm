from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from app.localization import COLUMN_LABELS, localized_value
from app.models import DuplicateDiscrepancy, Issue, ProcessingLog, RouteHistory, RouteRecord, StopRecord


def build_report(db: Session, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tables = {
        "Справочник маршрутов": _df(db, RouteRecord),
        "Ошибки и предупреждения": _df(db, Issue),
        "Дубли и расхождения": _df(db, DuplicateDiscrepancy),
        "Остановки": _df(db, StopRecord),
        "Журнал обработки": _df(db, ProcessingLog),
        "История изменений": _df(db, RouteHistory),
    }
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for sheet_name, frame in tables.items():
            frame.to_excel(writer, index=False, sheet_name=sheet_name)
            worksheet = writer.sheets[sheet_name]
            for column_cells in worksheet.columns:
                max_length = max(len(str(cell.value or "")) for cell in column_cells)
                worksheet.column_dimensions[column_cells[0].column_letter].width = min(max(max_length + 2, 12), 60)
    return output_path


def _df(db: Session, model: type) -> pd.DataFrame:
    rows = db.query(model).all()
    data = []
    for row in rows:
        item = {}
        for column in model.__table__.columns:
            value = getattr(row, column.name)
            item[COLUMN_LABELS.get(column.name, column.name)] = localized_value(value)
        data.append(item)
    return pd.DataFrame(data)
