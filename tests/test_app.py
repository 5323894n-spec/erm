from fastapi.testclient import TestClient

from app.main import app


def test_index_page_loads():
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert "ЭРМ маршруты" in response.text
