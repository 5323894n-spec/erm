from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ParsedIssue:
    severity: str
    code: str
    message: str


@dataclass
class ParsedStop:
    direction: str
    order_no: int
    stop_name: str
    streets: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    distance_m: float | None = None
    cumulative_distance_m: float | None = None
    travel_time_between_min: float | None = None
    cumulative_time_min: float | None = None


@dataclass
class ParsedRoute:
    route_number: str | None
    route_name: str | None
    file_name: str
    file_path: str
    sheet_name: str | None
    file_modified_at: datetime | None
    length_forward_km: float | None = None
    length_backward_km: float | None = None
    trip_time_forward_min: float | None = None
    trip_time_backward_min: float | None = None
    avg_speed_forward_kmh: float | None = None
    avg_speed_backward_kmh: float | None = None
    stops_forward_count: int = 0
    stops_backward_count: int = 0
    first_stop_forward: str | None = None
    last_stop_forward: str | None = None
    first_stop_backward: str | None = None
    last_stop_backward: str | None = None
    data_status: str = "ok"
    comment: str | None = None
    stops: list[ParsedStop] = field(default_factory=list)
    issues: list[ParsedIssue] = field(default_factory=list)
