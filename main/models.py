from .app import db
from typing import Dict, Any
from datetime import datetime
from sqlalchemy.orm import validates
import re

class Client(db.Model):
    __tablename__ = "client"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    credit_card = db.Column(db.String(50))
    car_number = db.Column(db.String(10))

    parking_logs = db.relationship(
        'Client_parking',
        backref='client',
        lazy=True)

    @validates('name', 'surname')
    def validate_name(self, key, value):
        if value is None:
            raise ValueError(f"Поле {key} не может быть пустым")
        
        # Проверяем, что в строке только буквы (или дефис для двойных фамилий)
        if not re.match(r"^[A-Za-zА-Яа-яЁё\- ]+$", str(value)):
            raise ValueError(f"Поле {key} содержит недопустимые символы: {value}")
            
        return value
    def __repr__(self):
        return f"Client {self.title}"

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in
                self.__table__.columns}

class Parking(db.Model):
    __tablename__ = "parking"

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), nullable=False)
    opened = db.Column(db.Boolean, default=True)
    count_places = db.Column(db.Integer, nullable=False)
    count_available_places = db.Column(db.Integer, nullable=False)

    client_logs = db.relationship(
        "Client_parking",
        backref="parking",
        lazy=True)
    
    @validates('count_available_places')
    def update_opened_status(self, key, value):
        # Если количество мест становится 0, закрываем парковку
        if value == 0:
            self.opened = False
        # Если места появились, открываем обратно
        elif value > 0:
            self.opened = True
        return value
    
    def __repr__(self):
        return f"Parking info {self.title}"

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in
                self.__table__.columns}

class Client_parking(db.Model):
    __tablename__ = "client_parking"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    parking_id = db.Column(db.Integer, db.ForeignKey('parking.id'))
    time_in = db.Column(db.DateTime)
    time_out = db.Column(db.DateTime)
    __table_args__ = (
        db.UniqueConstraint('client_id', 'parking_id', name='unique_client_parking'),
    )

    def __repr__(self):
        return f"<Client_parking {self.id}: Client {self.client_id} at Parking {self.parking_id}>"

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}