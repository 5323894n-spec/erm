COLUMN_LABELS = {
    "id": "ID",
    "route_id": "ID записи маршрута",
    "route_number": "Номер маршрута",
    "route_name": "Наименование маршрута",
    "file_name": "Имя файла",
    "file_path": "Путь к файлу",
    "sheet_name": "Название вкладки",
    "length_forward_km": "Протяженность прямого направления, км",
    "length_backward_km": "Протяженность обратного направления, км",
    "trip_time_forward_min": "Время рейса прямого направления, мин",
    "trip_time_backward_min": "Время рейса обратного направления, мин",
    "avg_speed_forward_kmh": "Средняя скорость прямого направления, км/ч",
    "avg_speed_backward_kmh": "Средняя скорость обратного направления, км/ч",
    "stops_forward_count": "Количество остановок в прямом направлении",
    "stops_backward_count": "Количество остановок в обратном направлении",
    "first_stop_forward": "Первая остановка прямого направления",
    "last_stop_forward": "Последняя остановка прямого направления",
    "first_stop_backward": "Первая остановка обратного направления",
    "last_stop_backward": "Последняя остановка обратного направления",
    "file_modified_at": "Дата изменения файла",
    "processed_at": "Дата обработки",
    "data_status": "Статус данных",
    "status": "Статус",
    "comment": "Комментарий",
    "is_actual": "Актуальная версия",
    "direction": "Направление",
    "order_no": "Порядковый номер",
    "stop_name": "Остановочный пункт",
    "streets": "Улицы следования",
    "latitude": "Широта",
    "longitude": "Долгота",
    "distance_m": "Расстояние между остановками, м",
    "cumulative_distance_m": "Расстояние нарастающим итогом, м",
    "travel_time_between_min": "Время движения между остановками, мин",
    "cumulative_time_min": "Время движения нарастающим итогом, мин",
    "severity": "Уровень",
    "code": "Код проверки",
    "message": "Сообщение",
    "created_at": "Дата создания",
    "current_route_id": "ID актуальной записи",
    "compared_route_id": "ID сравниваемой записи",
    "field_name": "Поле",
    "current_value": "Актуальное значение",
    "compared_value": "Сравниваемое значение",
    "changed_at": "Дата изменения",
    "changed_by": "Кем изменено",
    "old_value": "Старое значение",
    "new_value": "Новое значение",
}

FIELD_LABELS = {
    key: value for key, value in COLUMN_LABELS.items()
}

VALUE_LABELS = {
    "ok": "Без ошибок",
    "warning": "Предупреждение",
    "error": "Ошибка",
    "forward": "Прямое направление",
    "backward": "Обратное направление",
    "system": "Система",
    "user": "Пользователь",
    "True": "Да",
    "False": "Нет",
    True: "Да",
    False: "Нет",
}

ISSUE_CODE_LABELS = {
    "missing_parameters_sheet": "Отсутствует вкладка параметры",
    "missing_route_number": "Не найден номер маршрута",
    "missing_forward_direction": "Не найдено прямое направление",
    "missing_backward_direction": "Не найдено обратное направление",
    "missing_length_column": "Не найдена колонка протяженности",
    "missing_time_column": "Не найдена колонка времени",
    "zero_length": "Нулевая протяженность",
    "zero_trip_time": "Нулевое время рейса",
    "speed_too_low": "Средняя скорость ниже нормы",
    "speed_too_high": "Средняя скорость выше нормы",
    "direction_length_mismatch": "Расхождение направлений",
    "duplicate_route": "Дубль маршрута",
}


def localized_value(value):
    if value in VALUE_LABELS:
        return VALUE_LABELS[value]
    if isinstance(value, str) and value in ISSUE_CODE_LABELS:
        return ISSUE_CODE_LABELS[value]
    if isinstance(value, str) and value in FIELD_LABELS:
        return FIELD_LABELS[value]
    return value
