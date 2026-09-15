from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)
def test_get_residente_por_id():
    response = client.get("/residentes/1")
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "full_name": "Juan Perez",
        "tower": 1,
        "apartment": 101
    }
def test_get_residente_inexistente():
    response = client.get("/residentes/99")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Residente no encontrado"
    }
def test_get_residentes():
    response = client.get("/residentes")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "full_name": "Juan Perez",
            "tower": 1,
            "apartment": 101
        },
        {
            "id": 2,
            "full_name": "Maria Gomez",
            "tower": 2,
            "apartment": 305
        }
    ]


def test_get_residentes_por_torre():
    response = client.get("/residentes?tower=1")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "full_name": "Juan Perez",
            "tower": 1,
            "apartment": 101
        }
    ]


def test_get_residentes_torre_sin_coincidencias():
    response = client.get("/residentes?tower=99")

    assert response.status_code == 200
    assert response.json() == []


def test_crear_residente():
    response = client.post(
        "/residentes",
        json={
            "full_name": "Carlos Lopez",
            "tower": 1,
            "apartment": 205
        }
    )

    assert response.status_code == 201

    assert response.json() == {
        "id": 3,
        "full_name": "Carlos Lopez",
        "tower": 1,
        "apartment": 205
    }
def test_crear_residente_sin_nombre():
    response = client.post(
        "/residentes",
        json={
            "tower": 1,
            "apartment": 205
        }
    )

    assert response.status_code == 422