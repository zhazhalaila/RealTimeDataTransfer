import functools
from app import socketio, mqtt, db, create_mqtt_app
from app.events import bp
from flask_socketio import emit, send
from flask import has_app_context
from app.models import User, Sensor

ctx = create_mqtt_app().app_context()

@socketio.on('subscribe')
def handle_subcribe(data):
    mqtt.subscribe(str(data['topic']))
    print(mqtt.topics)
    print(has_app_context())

@socketio.on('unsubscribe')
def handle_unsubscribe(data):
    mqtt.unsubscribe(str(data['topic']))
    print(mqtt.topics)

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    with ctx:
        user = User.query.filter_by(mqtt_topic=message.topic).first()
        sensor = Sensor(sensor_value=message.payload.decode())
        user.sensors.append(sensor)
        db.session.add(user)
        db.session.commit()
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    socketio.emit(message.topic, data=data)