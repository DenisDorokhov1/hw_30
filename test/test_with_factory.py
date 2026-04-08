from .factories import ClientFactory, ParkingFactory
from main.models import Client, Parking

def test_factory_client(app, db):
    new_client = ClientFactory()
    db.session.commit()
    assert len(db.session.query(Client).all()) == 2
    assert isinstance(new_client.car_number, str)

def test_factory_parkig(app, db):
    new_parking = ParkingFactory()
    db.session.commit()
    assert len(db.session.query(Parking).all()) == 2
    assert isinstance(new_parking.count_places, int)
    assert new_parking.count_places == new_parking.count_available_places