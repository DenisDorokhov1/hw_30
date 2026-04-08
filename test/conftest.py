import pytest
from main.app import create_app, db as _db
from main.models import Client, Parking, Client_parking
from datetime import datetime

@pytest.fixture
def app():
    """Создаем образом самого приложения, формируем базу"""
    _app = create_app()
    _app.config["TESTING"] = True
    _app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://admin:admin@localhost:5432/parking_db"
    _app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    with _app.app_context():
        _db.create_all()
        client_1 = Client(
                    name="Peter",
                    surname="Parker",
                    credit_card='51516516161fsdfs',
                    car_number="FDd151sds")
        parking_1 = Parking(
                          address="Wall street 147",
                          count_places=100,
                          count_available_places=100)
        client_parking = Client_parking(
                        client_id=1,
                        parking_id=1,
                        time_in=datetime(2026, 4, 5, 12, 0, 0),
                        time_out=datetime(2026, 4, 6, 12, 0, 0)
                        )
        _db.session.add(client_1)
        _db.session.add(parking_1)
        _db.session.add(client_parking)
        _db.session.commit()

        yield _app
        _db.session.close()
        _db.drop_all()

@pytest.fixture
def client(app):
    """Образ клиента"""
    client = app.test_client()
    yield client

@pytest.fixture
def db(app):
    with app.app_context():
        yield _db