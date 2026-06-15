from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import DuplicateDiscrepancy, Issue, ProcessingLog, RouteHistory, RouteRecord, StopRecord
from app.schemas import ParsedRoute


COMPARISON_FIELDS = (
    "length_forward_km",
    "length_backward_km",
    "trip_time_forward_min",
    "trip_time_backward_min",
    "avg_speed_forward_kmh",
    "avg_speed_backward_kmh",
)


def save_parsed_route(db: Session, parsed: ParsedRoute) -> RouteRecord:
    route = RouteRecord(
        route_number=parsed.route_number,
        route_name=parsed.route_name,
        file_name=parsed.file_name,
        file_path=parsed.file_path,
        sheet_name=parsed.sheet_name,
        length_forward_km=parsed.length_forward_km,
        length_backward_km=parsed.length_backward_km,
        trip_time_forward_min=parsed.trip_time_forward_min,
        trip_time_backward_min=parsed.trip_time_backward_min,
        avg_speed_forward_kmh=parsed.avg_speed_forward_kmh,
        avg_speed_backward_kmh=parsed.avg_speed_backward_kmh,
        stops_forward_count=parsed.stops_forward_count,
        stops_backward_count=parsed.stops_backward_count,
        first_stop_forward=parsed.first_stop_forward,
        last_stop_forward=parsed.last_stop_forward,
        first_stop_backward=parsed.first_stop_backward,
        last_stop_backward=parsed.last_stop_backward,
        file_modified_at=parsed.file_modified_at,
        data_status=parsed.data_status,
        comment=parsed.comment,
    )
    db.add(route)
    db.flush()
    for stop in parsed.stops:
        db.add(
            StopRecord(
                route_id=route.id,
                route_number=parsed.route_number,
                direction=stop.direction,
                order_no=stop.order_no,
                stop_name=stop.stop_name,
                streets=stop.streets,
                latitude=stop.latitude,
                longitude=stop.longitude,
                distance_m=stop.distance_m,
                cumulative_distance_m=stop.cumulative_distance_m,
                travel_time_between_min=stop.travel_time_between_min,
                cumulative_time_min=stop.cumulative_time_min,
            )
        )
    for issue in parsed.issues:
        db.add(
            Issue(
                route_id=route.id,
                file_name=parsed.file_name,
                route_number=parsed.route_number,
                severity=issue.severity,
                code=issue.code,
                message=issue.message,
            )
        )
    db.add(ProcessingLog(file_name=parsed.file_name, file_path=parsed.file_path, status=parsed.data_status, comment=parsed.comment))
    db.commit()
    db.refresh(route)
    rebuild_duplicates(db)
    return route


def rebuild_duplicates(db: Session) -> None:
    db.execute(delete(DuplicateDiscrepancy))
    routes = db.scalars(select(RouteRecord).where(RouteRecord.route_number.is_not(None))).all()
    grouped: dict[str, list[RouteRecord]] = {}
    for route in routes:
        grouped.setdefault(str(route.route_number), []).append(route)

    for route_number, items in grouped.items():
        if len(items) < 2:
            for item in items:
                item.is_actual = True
            continue
        newest = max(items, key=lambda item: item.file_modified_at or item.processed_at)
        for item in items:
            item.is_actual = item.id == newest.id
        db.add(
            Issue(
                route_id=newest.id,
                file_name=newest.file_name,
                route_number=route_number,
                severity="warning",
                code="duplicate_route",
                message="Найдены дубли маршрута в разных файлах.",
            )
        )
        for item in items:
            if item.id == newest.id:
                continue
            for field in COMPARISON_FIELDS:
                current = getattr(newest, field)
                compared = getattr(item, field)
                if _different(current, compared):
                    db.add(
                        DuplicateDiscrepancy(
                            route_number=route_number,
                            current_route_id=newest.id,
                            compared_route_id=item.id,
                            field_name=field,
                            current_value=_value(current),
                            compared_value=_value(compared),
                            message=f"Поле {field} отличается между актуальным и старым файлом.",
                        )
                    )
    db.commit()


def update_route(db: Session, route_id: int, changes: dict[str, Any]) -> RouteRecord | None:
    route = db.get(RouteRecord, route_id)
    if route is None:
        return None
    allowed = {
        "route_number",
        "route_name",
        "length_forward_km",
        "length_backward_km",
        "trip_time_forward_min",
        "trip_time_backward_min",
        "avg_speed_forward_kmh",
        "avg_speed_backward_kmh",
        "data_status",
        "comment",
    }
    for field, new_value in changes.items():
        if field not in allowed:
            continue
        old_value = getattr(route, field)
        if str(old_value) != str(new_value):
            db.add(RouteHistory(route_id=route.id, route_number=route.route_number, changed_by="user", field_name=field, old_value=_value(old_value), new_value=_value(new_value), comment="Ручное исправление"))
            setattr(route, field, new_value)
    db.commit()
    db.refresh(route)
    rebuild_duplicates(db)
    return route


def confirm_route(db: Session, route_id: int) -> RouteRecord | None:
    route = db.get(RouteRecord, route_id)
    if route is None:
        return None
    if route.route_number:
        db.query(RouteRecord).filter(RouteRecord.route_number == route.route_number).update({"is_actual": False})
    route.is_actual = True
    db.add(RouteHistory(route_id=route.id, route_number=route.route_number, changed_by="user", field_name="is_actual", old_value="False", new_value="True", comment="Пользователь подтвердил актуальную версию"))
    db.commit()
    db.refresh(route)
    return route


def _different(left: Any, right: Any) -> bool:
    if left is None and right is None:
        return False
    if isinstance(left, float) or isinstance(right, float):
        try:
            return round(float(left or 0), 2) != round(float(right or 0), 2)
        except (TypeError, ValueError):
            return True
    return left != right


def _value(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat(sep=" ", timespec="seconds")
    return str(value)
