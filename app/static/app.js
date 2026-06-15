const state = {
  tab: "routes",
  data: [],
};

const endpoints = {
  routes: "/api/routes",
  issues: "/api/issues",
  duplicates: "/api/duplicates",
  stops: "/api/stops",
  logs: "/api/logs",
  history: "/api/history",
};

const routeEditable = new Set([
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
]);

const columnLabels = {
  id: "ID",
  route_id: "ID записи маршрута",
  route_number: "Номер маршрута",
  route_name: "Наименование маршрута",
  file_name: "Имя файла",
  file_path: "Путь к файлу",
  sheet_name: "Название вкладки",
  length_forward_km: "Протяженность прямого направления, км",
  length_backward_km: "Протяженность обратного направления, км",
  trip_time_forward_min: "Время рейса прямого направления, мин",
  trip_time_backward_min: "Время рейса обратного направления, мин",
  avg_speed_forward_kmh: "Средняя скорость прямого направления, км/ч",
  avg_speed_backward_kmh: "Средняя скорость обратного направления, км/ч",
  stops_forward_count: "Количество остановок в прямом направлении",
  stops_backward_count: "Количество остановок в обратном направлении",
  first_stop_forward: "Первая остановка прямого направления",
  last_stop_forward: "Последняя остановка прямого направления",
  first_stop_backward: "Первая остановка обратного направления",
  last_stop_backward: "Последняя остановка обратного направления",
  file_modified_at: "Дата изменения файла",
  processed_at: "Дата обработки",
  data_status: "Статус данных",
  status: "Статус",
  comment: "Комментарий",
  is_actual: "Актуальная версия",
  direction: "Направление",
  order_no: "Порядковый номер",
  stop_name: "Остановочный пункт",
  streets: "Улицы следования",
  latitude: "Широта",
  longitude: "Долгота",
  distance_m: "Расстояние между остановками, м",
  cumulative_distance_m: "Расстояние нарастающим итогом, м",
  travel_time_between_min: "Время движения между остановками, мин",
  cumulative_time_min: "Время движения нарастающим итогом, мин",
  severity: "Уровень",
  code: "Код проверки",
  message: "Сообщение",
  created_at: "Дата создания",
  current_route_id: "ID актуальной записи",
  compared_route_id: "ID сравниваемой записи",
  field_name: "Поле",
  current_value: "Актуальное значение",
  compared_value: "Сравниваемое значение",
  changed_at: "Дата изменения",
  changed_by: "Кем изменено",
  old_value: "Старое значение",
  new_value: "Новое значение",
};

const valueLabels = {
  ok: "Без ошибок",
  warning: "Предупреждение",
  error: "Ошибка",
  forward: "Прямое направление",
  backward: "Обратное направление",
  true: "Да",
  false: "Нет",
  system: "Система",
  user: "Пользователь",
};

const issueCodeLabels = {
  missing_parameters_sheet: "Отсутствует вкладка параметры",
  missing_route_number: "Не найден номер маршрута",
  missing_forward_direction: "Не найдено прямое направление",
  missing_backward_direction: "Не найдено обратное направление",
  missing_length_column: "Не найдена колонка протяженности",
  missing_time_column: "Не найдена колонка времени",
  zero_length: "Нулевая протяженность",
  zero_trip_time: "Нулевое время рейса",
  speed_too_low: "Средняя скорость ниже нормы",
  speed_too_high: "Средняя скорость выше нормы",
  direction_length_mismatch: "Расхождение направлений",
  duplicate_route: "Дубль маршрута",
};

const reverseValueLabels = Object.fromEntries(Object.entries(valueLabels).map(([key, value]) => [value, key]));

document.querySelectorAll(".tabs button").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".tabs button").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    state.tab = button.dataset.tab;
    loadData();
  });
});

document.getElementById("applyFilters").addEventListener("click", () => loadData());

async function loadData() {
  let url = endpoints[state.tab];
  if (state.tab === "routes") {
    const params = new URLSearchParams();
    const route = document.getElementById("filterRoute").value.trim();
    const status = document.getElementById("filterStatus").value;
    const file = document.getElementById("filterFile").value.trim();
    const hasErrors = document.getElementById("filterErrors").checked;
    if (route) params.set("route_number", route);
    if (status) params.set("status", status);
    if (file) params.set("file_name", file);
    if (hasErrors) params.set("has_errors", "true");
    url += `?${params.toString()}`;
  }
  const response = await fetch(url);
  state.data = await response.json();
  renderTable();
}

function renderTable() {
  const head = document.getElementById("tableHead");
  const body = document.getElementById("tableBody");
  body.innerHTML = "";
  if (!state.data.length) {
    head.innerHTML = "<tr><th>Нет данных</th></tr>";
    return;
  }
  const keys = Object.keys(state.data[0]);
  head.innerHTML = `<tr>${keys.map((key) => `<th>${labelFor(key)}</th>`).join("")}${state.tab === "routes" ? "<th>Действия</th>" : ""}</tr>`;
  state.data.forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = keys.map((key) => cell(row, key)).join("");
    if (state.tab === "routes") {
      const td = document.createElement("td");
      const button = document.createElement("button");
      button.textContent = "Подтвердить";
      button.addEventListener("click", () => confirmRoute(row.id));
      td.appendChild(button);
      tr.appendChild(td);
    }
    body.appendChild(tr);
  });
}

function cell(row, key) {
  const value = row[key] ?? "";
  const editable = state.tab === "routes" && routeEditable.has(key);
  const className = key === "data_status" ? `status-${value}` : "";
  const editAttrs = editable ? `contenteditable="true" onblur="saveCell(${row.id}, '${key}', this.innerText)"` : "";
  return `<td class="${className}" ${editAttrs}>${escapeHtml(displayValue(key, value))}</td>`;
}

async function saveCell(id, key, value) {
  await fetch(`/api/routes/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ [key]: coerce(reverseValueLabels[value.trim()] || value) }),
  });
  loadData();
}

async function confirmRoute(id) {
  await fetch(`/api/routes/${id}/confirm`, { method: "POST" });
  loadData();
}

function coerce(value) {
  const trimmed = value.trim();
  if (trimmed === "") return null;
  const number = Number(trimmed.replace(",", "."));
  return Number.isFinite(number) && /^-?\d+([,.]\d+)?$/.test(trimmed) ? number : trimmed;
}

function labelFor(key) {
  return columnLabels[key] || key;
}

function displayValue(key, value) {
  if (key === "field_name" && columnLabels[value]) {
    return columnLabels[value];
  }
  if (key === "code" && issueCodeLabels[value]) {
    return issueCodeLabels[value];
  }
  const normalized = String(value);
  return valueLabels[normalized] || normalized;
}

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "\"": "&quot;",
    "'": "&#039;",
  }[char]));
}

loadData();
