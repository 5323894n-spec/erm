from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shutil
from uuid import uuid4

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import BASE_DIR, REPORT_DIR, UPLOAD_DIR
from app.db import get_db, init_db
from app.exporter import build_report
from app.models import DuplicateDiscrepancy, Issue, ProcessingLog, RouteHistory, RouteRecord, StopRecord
from app.parser import parse_workbook
from app.services import confirm_route, save_parsed_route, update_route


app = FastAPI(title="ЭРМ маршруты", version="1.0.0")
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "app" / "static")), name="static")
init_db()


@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    stats = {
        "routes": db.query(RouteRecord).count(),
        "issues": db.query(Issue).count(),
        "duplicates": db.query(DuplicateDiscrepancy).count(),
        "logs": db.query(ProcessingLog).count(),
    }
    return templates.TemplateResponse(request, "index.html", {"stats": stats})


@app.post("/upload")
async def upload_files(files: list[UploadFile] = File(...), db: Session = Depends(get_db)):
    processed = 0
    for upload in files:
        if not upload.filename.lower().endswith(".xlsx"):
            continue
        safe_name = Path(upload.filename).name
        target = UPLOAD_DIR / f"{uuid4().hex}_{safe_name}"
        with target.open("wb") as buffer:
            shutil.copyfileobj(upload.file, buffer)
        modified_at = datetime.fromtimestamp(target.stat().st_mtime)
        parsed = parse_workbook(target, original_path=upload.filename, modified_at=modified_at)
        save_parsed_route(db, parsed)
        processed += 1
    return RedirectResponse(url=f"/?processed={processed}", status_code=303)


@app.get("/api/routes")
def routes(
    route_number: str | None = None,
    status: str | None = None,
    file_name: str | None = None,
    has_errors: bool | None = None,
    processed_from: str | None = None,
    db: Session = Depends(get_db),
):
    query = select(RouteRecord).order_by(RouteRecord.processed_at.desc())
    if route_number:
        query = query.where(RouteRecord.route_number.contains(route_number))
    if status:
        query = query.where(RouteRecord.data_status == status)
    if file_name:
        query = query.where(RouteRecord.file_name.contains(file_name))
    if processed_from:
        query = query.where(RouteRecord.processed_at >= datetime.fromisoformat(processed_from))
    items = db.scalars(query).all()
    if has_errors is True:
        issue_route_ids = {row[0] for row in db.query(Issue.route_id).filter(Issue.severity == "error").all()}
        items = [item for item in items if item.id in issue_route_ids]
    return [_serialize(item) for item in items]


@app.patch("/api/routes/{route_id}")
async def edit_route(route_id: int, request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    route = update_route(db, route_id, payload)
    if route is None:
        raise HTTPException(status_code=404, detail="Route not found")
    return _serialize(route)


@app.post("/api/routes/{route_id}/confirm")
def confirm(route_id: int, db: Session = Depends(get_db)):
    route = confirm_route(db, route_id)
    if route is None:
        raise HTTPException(status_code=404, detail="Route not found")
    return _serialize(route)


@app.get("/api/issues")
def issues(db: Session = Depends(get_db)):
    return [_serialize(item) for item in db.query(Issue).order_by(Issue.created_at.desc()).all()]


@app.get("/api/duplicates")
def duplicates(db: Session = Depends(get_db)):
    return [_serialize(item) for item in db.query(DuplicateDiscrepancy).order_by(DuplicateDiscrepancy.created_at.desc()).all()]


@app.get("/api/logs")
def logs(db: Session = Depends(get_db)):
    return [_serialize(item) for item in db.query(ProcessingLog).order_by(ProcessingLog.processed_at.desc()).all()]


@app.get("/api/history")
def history(db: Session = Depends(get_db)):
    return [_serialize(item) for item in db.query(RouteHistory).order_by(RouteHistory.changed_at.desc()).all()]


@app.get("/api/stops")
def stops(db: Session = Depends(get_db)):
    return [_serialize(item) for item in db.query(StopRecord).order_by(StopRecord.route_number, StopRecord.direction, StopRecord.order_no).all()]


@app.post("/process-folder")
def process_folder(folder_path: str = Form(...), db: Session = Depends(get_db)):
    root = Path(folder_path)
    if not root.exists() or not root.is_dir():
        raise HTTPException(status_code=400, detail="Folder not found")
    processed = 0
    for path in root.rglob("*.xlsx"):
        parsed = parse_workbook(path, original_path=str(path), modified_at=datetime.fromtimestamp(path.stat().st_mtime))
        save_parsed_route(db, parsed)
        processed += 1
    return RedirectResponse(url=f"/?processed={processed}", status_code=303)


@app.get("/export")
def export(db: Session = Depends(get_db)):
    output = REPORT_DIR / f"erm_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    build_report(db, output)
    return FileResponse(output, filename=output.name, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


def _serialize(row):
    data = {}
    for column in row.__table__.columns:
        value = getattr(row, column.name)
        data[column.name] = value.isoformat(sep=" ", timespec="seconds") if isinstance(value, datetime) else value
    return data
