import pytest


def esperado(persona_id, nombre="Residente de prueba"):
    return {
        "id": persona_id,
        "full_name": nombre,
        "tower": 1,
        "apartment": "101",
    }


def test_consultar_por_id(api):
    cliente, persona_id = api

    respuesta = cliente.get(f"/residentes/{persona_id}")

    assert respuesta.status_code == 200
    assert respuesta.json() == esperado(persona_id)


@pytest.mark.parametrize(
    "ruta,hay_resultados",
    [
        ("/residentes", True),
        ("/residentes?tower=1", True),
        ("/residentes?tower=99", False),
    ],
)
def test_listado_y_filtro(api, ruta, hay_resultados):
    cliente, persona_id = api

    respuesta = cliente.get(ruta)

    assert respuesta.status_code == 200
    datos = [esperado(persona_id)] if hay_resultados else []
    assert respuesta.json() == datos


@pytest.mark.parametrize("metodo", ["GET", "PUT", "DELETE"])
def test_residente_inexistente(api, metodo):
    cliente, _ = api
    opciones = {}

    if metodo == "PUT":
        opciones["json"] = {
            "full_name": "Nombre de prueba",
            "tower": 1,
            "apartment": 101,
        }

    respuesta = cliente.request(
        metodo, "/residentes/-1", **opciones
    )

    assert respuesta.status_code == 404
    assert respuesta.json() == {
        "detail": "Residente no encontrado"
    }


def test_crear_residente(api):
    cliente, _ = api

    respuesta = cliente.post("/residentes", json={
        "full_name": "Nueva persona",
        "tower": 1,
        "apartment": 101,
    })

    assert respuesta.status_code == 201
    persona_id = respuesta.json()["id"]
    assert respuesta.json() == esperado(
        persona_id, "Nueva persona"
    )

    consulta = cliente.get(f"/residentes/{persona_id}")
    assert consulta.status_code == 200
    assert consulta.json() == respuesta.json()


def test_actualizar_residente(api):
    cliente, persona_id = api

    respuesta = cliente.put(
        f"/residentes/{persona_id}",
        json={
            "full_name": "Nombre actualizado",
            "tower": 1,
            "apartment": 101,
        },
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == esperado(
        persona_id, "Nombre actualizado"
    )

    consulta = cliente.get(f"/residentes/{persona_id}")
    assert consulta.json() == respuesta.json()


def test_eliminar_residente(api):
    cliente, persona_id = api

    respuesta = cliente.delete(f"/residentes/{persona_id}")

    assert respuesta.status_code == 204
    assert respuesta.content == b""
    assert cliente.get(
        f"/residentes/{persona_id}"
    ).status_code == 404


@pytest.mark.parametrize("campo", [
    "full_name", "tower", "apartment"
])
def test_campos_obligatorios(api, campo):
    cliente, _ = api
    datos = {
        "full_name": "Persona incompleta",
        "tower": 1,
        "apartment": 101,
    }
    datos.pop(campo)

    respuesta = cliente.post("/residentes", json=datos)

    assert respuesta.status_code == 422
