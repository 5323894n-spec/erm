from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class RouteRecord(Base):
    __tablename__ = "route_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    route_number: Mapped[str | None] = mapped_column(String(32), index=True)
    route_name: Mapped[str | None] = mapped_column(String(512))
    file_name: Mapped[str] = mapped_column(String(512))
    file_path: Mapped[str] = mapped_column(Text)
    sheet_name: Mapped[str | None] = mapped_column(String(255))
    length_forward_km: Mapped[float | None] = mapped_column(Float)
    length_backward_km: Mapped[float | None] = mapped_column(Float)
    trip_time_forward_min: Mapped[float | None] = mapped_column(Float)
    trip_time_backward_min: Mapped[float | None] = mapped_column(Float)
    avg_speed_forward_kmh: Mapped[float | None] = mapped_column(Float)
    avg_speed_backward_kmh: Mapped[float | None] = mapped_column(Float)
    stops_forward_count: Mapped[int] = mapped_column(Integer, default=0)
    stops_backward_count: Mapped[int] = mapped_column(Integer, default=0)
    first_stop_forward: Mapped[str | None] = mapped_column(String(512))
    last_stop_forward: Mapped[str | None] = mapped_column(String(512))
    first_stop_backward: Mapped[str | None] = mapped_column(String(512))
    last_stop_backward: Mapped[str | None] = mapped_column(String(512))
    file_modified_at: Mapped[datetime | None] = mapped_column(DateTime)
    processed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    data_status: Mapped[str] = mapped_column(String(32), default="ok", index=True)
    comment: Mapped[str | None] = mapped_column(Text)
    is_actual: Mapped[bool] = mapped_column(default=False, index=True)

    stops: Mapped[list["StopRecord"]] = relationship(back_populates="route", cascade="all, delete-orphan")
    issues: Mapped[list["Issue"]] = relationship(back_populates="route", cascade="all, delete-orphan")


class StopRecord(Base):
    __tablename__ = "stop_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    route_id: Mapped[int] = mapped_column(ForeignKey("route_records.id"), index=True)
    route_number: Mapped[str | None] = mapped_column(String(32), index=True)
    direction: Mapped[str] = mapped_column(String(16))
    order_no: Mapped[int] = mapped_column(Integer)
    stop_name: Mapped[str] = mapped_column(String(512))
    streets: Mapped[str | None] = mapped_column(Text)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    distance_m: Mapped[float | None] = mapped_column(Float)
    cumulative_distance_m: Mapped[float | None] = mapped_column(Float)
    travel_time_between_min: Mapped[float | None] = mapped_column(Float)
    cumulative_time_min: Mapped[float | None] = mapped_column(Float)

    route: Mapped[RouteRecord] = relationship(back_populates="stops")


class Issue(Base):
    __tablename__ = "issues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    route_id: Mapped[int | None] = mapped_column(ForeignKey("route_records.id"), nullable=True, index=True)
    file_name: Mapped[str] = mapped_column(String(512))
    route_number: Mapped[str | None] = mapped_column(String(32), index=True)
    severity: Mapped[str] = mapped_column(String(16), index=True)
    code: Mapped[str] = mapped_column(String(64), index=True)
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    route: Mapped[RouteRecord | None] = relationship(back_populates="issues")


class DuplicateDiscrepancy(Base):
    __tablename__ = "duplicate_discrepancies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    route_number: Mapped[str] = mapped_column(String(32), index=True)
    current_route_id: Mapped[int] = mapped_column(Integer)
    compared_route_id: Mapped[int] = mapped_column(Integer)
    field_name: Mapped[str] = mapped_column(String(64))
    current_value: Mapped[str | None] = mapped_column(String(255))
    compared_value: Mapped[str | None] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class ProcessingLog(Base):
    __tablename__ = "processing_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    file_name: Mapped[str] = mapped_column(String(512), index=True)
    file_path: Mapped[str] = mapped_column(Text)
    processed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    comment: Mapped[str | None] = mapped_column(Text)


class RouteHistory(Base):
    __tablename__ = "route_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    route_id: Mapped[int] = mapped_column(Integer, index=True)
    route_number: Mapped[str | None] = mapped_column(String(32), index=True)
    changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    changed_by: Mapped[str] = mapped_column(String(64), default="system")
    field_name: Mapped[str] = mapped_column(String(64))
    old_value: Mapped[str | None] = mapped_column(Text)
    new_value: Mapped[str | None] = mapped_column(Text)
    comment: Mapped[str | None] = mapped_column(Text)
