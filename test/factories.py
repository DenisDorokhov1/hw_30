import factory
import factory.fuzzy as fuzzy

from main.app import db
from main.models import Client, Parking

class ClientFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Client
        sqlalchemy_session = db.session
    name = factory.Faker('first_name')
    surname = factory.Faker('last_name')
    # Генерируем случайную карту (16 цифр)
    credit_card = fuzzy.FuzzyText(length=16, chars="0123456789")
    
    # Генерируем номер машины (например, формат А123АА)
    car_number = fuzzy.FuzzyText(length=6, chars="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")

class ParkingFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Parking
        sqlalchemy_session = db.session
    
    address = factory.Faker("address")
    opened = True
    count_places = fuzzy.FuzzyInteger(10, 100)
    # Делаем так, чтобы доступных мест изначально было столько же, сколько всего
    count_available_places = factory.SelfAttribute('count_places')