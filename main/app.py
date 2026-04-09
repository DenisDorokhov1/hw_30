from datetime import datetime

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        """postgresql://admin:admin@localhost:5432/parking_db"""
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    from .models import Client, Client_parking, Parking

    with app.app_context():
        db.create_all()

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    @app.route("/clients", methods=["GET"])
    def get_all_clients():
        """Получение клиентов"""
        clients = db.session.query(Client).all()
        clients_list = [i_client.to_json() for i_client in clients]
        return jsonify(clients_list), 200

    @app.route("/clients/<int:client_id>", methods=["GET"])
    def get_client_by_id(client_id: int):
        """Получить инфу про клиента по id"""
        client = db.session.get(Client, client_id)
        return jsonify(client.to_json()), 200  # type: ignore

    @app.route("/clients", methods=["POST"])
    def create_client():
        """Создать нового клиента"""
        name = request.form.get("name", type=str)
        surname = request.form.get("surname", type=str)
        credit_card = request.form.get("credit_card", type=str)
        car_number = request.form.get("car_number", type=str)

        try:
            new_client = Client(
                name=name,
                surname=surname,
                credit_card=credit_card,
                car_number=car_number,
            )
            db.session.add(new_client)
            db.session.commit()
        except ValueError as ex:
            return jsonify({"error": str(ex)}), 400

        return jsonify(f"Created new user {new_client.name}"), 201

    @app.route("/parking", methods=["POST"])
    def create_parking():
        """Создаем парковочную зону"""
        address = request.form.get("address", type=str)
        count_places = request.form.get("count_places", type=int)
        count_available_places = request.form.get("count_available_places", type=int)

        if not address or address.strip() == "":
            return (
                jsonify({"error": "Field 'address' must be a non-empty string"}),
                400,
            )

        if count_places is None:
            return (
                jsonify({"error": "Field 'count_places' must be an integer"}),
                400,
            )

        if count_available_places is None:
            return (
                jsonify({"error": "Field 'count_available_places' must be an integer"}),
                400,
            )

        if count_available_places > count_places:
            return (
                jsonify({"error": "Available places cannot exceed total places"}),
                400,
            )

        new_parking = Parking(
            address=address,
            count_places=count_places,
            count_available_places=count_available_places,
        )
        db.session.add(new_parking)
        db.session.commit()

        return jsonify(f"Created new parking zone {new_parking.address}"), 201

    @app.route("/client_parking", methods=["POST"])
    def client_parkings():
        "Заезд на парковку"
        client_id = request.form.get("client_id")
        parking_id = request.form.get("parking_id")

        # проверяем, что такой клиент и паркинг есть
        client = db.session.get(Client, client_id)
        if not client:
            return jsonify({"error": f"There is no client {client_id}"}), 400
        parking = db.session.get(Parking, parking_id)
        if not parking:
            return jsonify({"error": f"There is no parking {parking_id}"}), 400

        # проверяем открыта ли парковка
        open_or_not = (
            db.session.query(Parking.opened).filter(Parking.id == parking_id).scalar()
        )
        if open_or_not is False:
            return jsonify({"error": f"Parking {parking_id} is occupied"}), 400

        # уменьшаем кол-во парковочных мест
        parking.count_available_places -= 1
        # фиксируем дату заезда
        current_datetime = datetime.now()

        new_client_parking = Client_parking(
            client_id=client_id,
            parking_id=parking_id,
            time_in=current_datetime,
        )
        db.session.add(new_client_parking)
        db.session.commit()

        return (
            jsonify({"message": f"""Car {new_client_parking.client.car_number} is
              parked in {new_client_parking.parking.address}"""}),
            201,
        )

    @app.route("/client_parking", methods=["DELETE"])
    def leaving_parking():
        """Выезд из парковки"""
        client_id = request.form.get("client_id")
        parking_id = request.form.get("parking_id")

        # проверяем, что такой клиент (его карта) и паркинг есть
        client = db.session.get(Client, client_id)
        if not client:
            return jsonify({"error": f"There is no client {client_id}"}), 404
        if not client.credit_card:
            return (
                jsonify({"error": f"There is no credit card info of user {client_id}"}),
                400,
            )
        parking = db.session.get(Parking, parking_id)
        if not parking:
            return jsonify({"error": f"There is no parking {parking_id}"}), 400

        # увеличиваем, кол-во доступных парковочных мест
        parking.count_available_places += 1

        # находим последнюю запись, где клиент парковался с пустой датой выезда
        log_entry = Client_parking.query.filter_by(
            client_id=client_id, parking_id=parking_id, time_out=None
        ).first()

        if not log_entry:
            return jsonify({"error": "Active parking session not found"}), 404

        leaving_date = datetime.now()
        log_entry.time_out = leaving_date
        db.session.commit()

        return (
            jsonify({"message": f"""Car {log_entry.client.car_number} is
              leaving parking in {log_entry.parking.address}"""}),
            201,
        )

    return app
