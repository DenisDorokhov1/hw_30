import pytest

from main.app import db
from main.models import Parking


@pytest.mark.parametrize("route", ["/clients", "clients/1"])
def test_route_status(client, route):
    rv = client.get(route)
    assert rv.status_code == 200


def test_client(client) -> None:
    user_data = {
        "name": "Bruce",
        "surname": "Wayne",
        "credit_card": "145fsdfsfa",
        "car_number": "G1214L12",
    }
    resp = client.post("/clients", data=user_data)

    assert resp.status_code == 201


def test_client_error(client):
    """Тест, что без имени выйдет ошибка"""
    user_data = {"credit_card": "145fsdfsfa", "car_number": "G1214L12"}
    resp = client.post("/clients", data=user_data)

    assert resp.status_code == 400
    assert "не может быть пустым" in resp.get_json()["error"]


def test_client_name_error(client):
    """Тест, что если имя будет не строкой, выйдет ошибка"""
    user_data = {
        "name": 123,
        "surname": "Wayne",
        "credit_card": "145fsdfsfa",
        "car_number": "G1214L12",
    }
    resp = client.post("/clients", data=user_data)

    assert resp.status_code == 400
    assert "содержит недопустимые символы" in resp.get_json()["error"]


def test_parking(client) -> None:
    parking_data = {"address": "Gotham", "count_places": 2, "count_available_places": 2}
    resp = client.post("/parking", data=parking_data)

    assert resp.status_code == 201


def test_parking_error(client):
    """Тест, что без данных об адресе парковка не создастся"""
    parking_data = {"count_places": 2, "count_available_places": 2}
    resp = client.post("/parking", data=parking_data)

    assert resp.status_code == 400
    assert "a non-empty string" in resp.get_json()["error"]


def test_count_error(client):
    """Тест, что если кол-во мест - символы, то парковка не создастся"""
    parking_data = {
        "address": "Novaya street 15",
        "count_places": "abcd",
        "count_available_places": 2,
    }
    resp = client.post("/parking", data=parking_data)

    assert resp.status_code == 400
    assert "'count_places' must be an integer" in resp.get_json()["error"]


def test_available_places_error(client):
    """Тест, что если кол-во свободных мест - символы, то парковка не создастся"""
    parking_data = {
        "address": "Novaya street 15",
        "count_places": 14,
        "count_available_places": "abcd",
    }
    resp = client.post("/parking", data=parking_data)

    assert resp.status_code == 400
    assert "'count_available_places' must be an integer" in resp.get_json()["error"]


def test_num_places_error(client):
    """Тест, что кол-во допустных мест не должно быть больше общего кол-ва мест"""
    parking_data = {
        "address": "Novaya street 15",
        "count_places": 14,
        "count_available_places": 30,
    }
    resp = client.post("/parking", data=parking_data)

    assert resp.status_code == 400
    assert "Available places cannot exceed total places" in resp.get_json()["error"]


@pytest.mark.parking
def test_parking_car_entry(client):
    """Паркуемся"""
    # создаем для начала своего клиента и парковку
    user_data = {
        "name": "Clark",
        "surname": "Kent",
        "credit_card": "51561fdvfdf",
        "car_number": "Sma11vi11e",
    }
    client.post("/clients", data=user_data)
    parking_data = {
        "address": "Metropolice",
        "count_places": 5,
        "count_available_places": 1,
    }
    client.post("/parking", data=parking_data)
    # паркуем созданного пользователя в парковку
    data = {"client_id": 2, "parking_id": 2}
    resp = client.post("/client_parking", data=data)

    assert resp.status_code == 201
    assert "parked in" in resp.get_json()["message"]


@pytest.mark.parking
def test_no_client_id(client):
    """Тест, что без id клиента выйдет ошибка"""
    # паркуем несуществующего пользователя в парковку
    data = {"client_id": 2, "parking_id": 1}
    resp = client.post("/client_parking", data=data)

    assert resp.status_code == 400
    assert "There is no client" in resp.get_json()["error"]


@pytest.mark.parking
def test_no_parking_id(client):
    """Тест, что без id парковки выйдет ошибка"""
    # паркуем пользователя в несуществующую парковку
    data = {"client_id": 1, "parking_id": 2}
    resp = client.post("/client_parking", data=data)

    assert resp.status_code == 400
    assert "There is no parking" in resp.get_json()["error"]


@pytest.mark.parking
def test_full_parking_id(client):
    """Тест, что нельзя заехать в занятую парковку"""
    user_data = {
        "name": "Clark",
        "surname": "Kent",
        "credit_card": "51561fdvfdf",
        "car_number": "Sma11vi11e",
    }
    client.post("/clients", data=user_data)
    parking_data = {
        "address": "Metropolice",
        "count_places": 5,
        "count_available_places": 1,
    }
    client.post("/parking", data=parking_data)
    # паркуем созданного пользователя в парковку
    data_1 = {"client_id": 2, "parking_id": 2}
    client.post("/client_parking", data=data_1)
    # создаем нового пользователя
    user_data_2 = {
        "name": "Bruce",
        "surname": "Wayne",
        "credit_card": "145fsdfsfa",
        "car_number": "G1214L12",
    }
    resp = client.post("/clients", data=user_data_2)
    # пробуем его припарковать на новую праковку, которая должна быть закрытой
    data_2 = {"client_id": 3, "parking_id": 2}
    resp = client.post("/client_parking", data=data_2)

    assert resp.status_code == 400
    assert "is occupied" in resp.get_json()["error"]


@pytest.mark.parking
def test_leaving_parking(client):
    """Тест выезда с парковки"""
    # создаем для начала своего клиента и парковку
    user_data = {
        "name": "Clark",
        "surname": "Kent",
        "credit_card": "51561fdvfdf",
        "car_number": "Sma11vi11e",
    }
    client.post("/clients", data=user_data)
    parking_data = {
        "address": "Metropolice",
        "count_places": 5,
        "count_available_places": 1,
    }
    client.post("/parking", data=parking_data)
    # паркуем созданного пользователя и вывозим его
    user_parking = {"client_id": 2, "parking_id": 2}
    resp = client.post("/client_parking", data=user_parking)
    user_leaving = {"client_id": 2, "parking_id": 2}
    resp = client.delete("/client_parking", data=user_leaving)

    assert resp.status_code == 201
    assert "leaving parking in" in resp.get_json()["message"]


@pytest.mark.parking
def test_occupied(client):
    """Заезд на парковку, которая уже занята"""

    parking_data = {
        "address": "Full Street 1",
        "count_places": 10,
        "count_available_places": 0,
    }
    client.post("/parking", data=parking_data)

    user_data = {
        "name": "Bane",
        "surname": "Villain",
        "credit_card": "666",
        "car_number": "DARKNESS",
    }
    client.post("/clients", data=user_data)

    data = {"client_id": 2, "parking_id": 2}
    resp = client.post("/client_parking", data=data)

    assert resp.status_code == 400
    assert "occupied" in resp.get_json()["error"]


@pytest.mark.parking
def test_less_parking_space(client, app):
    """Тест, что при въезде на парковку кол-во мест уменьшается"""
    parking_data = {
        "address": "Full Street 1",
        "count_places": 10,
        "count_available_places": 10,
    }
    client.post("/parking", data=parking_data)

    initial_places = parking_data["count_available_places"]
    # Запрос на заезд
    data = {"client_id": 1, "parking_id": 2}
    client.post("/client_parking", data=data)

    with app.app_context():
        # берем инфу про id=2 парковочное место
        parking_after = db.session.get(Parking, 2)
        final_places = parking_after.count_available_places

    # Проверяем, что стало на 1 меньше
    assert final_places == initial_places - 1


@pytest.mark.parking
def test_equal_num_parking_space(client, app):
    """Тест, что при выезде с парковки кол-во мест возвращается к прежнему кол-ву"""
    # создаем новое парковочное место
    parking_data = {
        "address": "Full Street 1",
        "count_places": 10,
        "count_available_places": 10,
    }
    client.post("/parking", data=parking_data)

    initial_places = parking_data["count_available_places"]
    # Запрос на заезд
    data = {"client_id": 1, "parking_id": 2}
    # заезжаем на парковку
    client.post("/client_parking", data=data)
    # выезжаем из парковки
    client.delete("/client_parking", data=data)

    with app.app_context():
        # берем инфу про id=2 парковочное место
        parking_after = db.session.get(Parking, 2)
        final_places = parking_after.count_available_places

    # Проверяем, кол-во мест после заезда и выезда осталось таким же
    assert final_places == initial_places


@pytest.mark.parking
def test_no_card(client):
    """Тест, что при выезде без инфы про карту, выйдет ошибка"""
    user_data = {"name": "Bane", "surname": "Villain", "car_number": "DARKNESS"}
    client.post("/clients", data=user_data)

    data = {"client_id": 2, "parking_id": 1}
    client.post("/client_parking", data=data)
    resp = client.delete("/client_parking", data=data)

    assert resp.status_code == 400
    assert "no credit card" in resp.get_json()["error"]


# запуск по маркеру: pytest -m parking
