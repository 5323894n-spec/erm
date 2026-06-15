from datetime import datetime
from pathlib import Path

from openpyxl import Workbook

from app.parser import parse_workbook, route_number_from_filename, time_to_minutes


def test_route_number_from_filename():
    assert route_number_from_filename("ЭРМ_М001_20240101.xlsx") == "1"


def test_time_to_minutes_from_string_and_excel_fraction():
    assert time_to_minutes("00:51") == 51
    assert time_to_minutes(0.5) == 720


def test_parse_workbook_extracts_route_metrics(tmp_path: Path):
    path = tmp_path / "ЭРМ_М001_20240101.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.title = "Параметры"
    ws.append(['Маршрут № 1 "Вокзал - Ореховая улица"'])
    ws.append(["прямое направление"])
    ws.append(["остановочный пункт", "наименования улиц", "широта", "долгота", "общ программн", "время движения нарастающ"])
    ws.append(["А", "Ленина", 55.1, 37.1, 0, "00:00"])
    ws.append(["Б", "Мира", 55.2, 37.2, 12000, "00:36"])
    ws.append(["обратное направление"])
    ws.append(["остановочный пункт", "наименования улиц", "широта", "долгота", "общ программн", "время движения нарастающ"])
    ws.append(["Б", "Мира", 55.2, 37.2, 0, "00:00"])
    ws.append(["А", "Ленина", 55.1, 37.1, 10000, "00:30"])
    wb.save(path)

    result = parse_workbook(path, modified_at=datetime(2024, 1, 1))

    assert result.route_number == "1"
    assert result.route_name == "Вокзал - Ореховая улица"
    assert result.length_forward_km == 12
    assert result.length_backward_km == 10
    assert result.trip_time_forward_min == 36
    assert result.trip_time_backward_min == 30
    assert result.avg_speed_forward_kmh == 20
    assert result.stops_forward_count == 2
    assert result.first_stop_forward == "А"
    assert result.last_stop_backward == "А"
    assert result.data_status in {"ok", "warning"}
