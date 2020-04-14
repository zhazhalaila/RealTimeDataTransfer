from dateutil import parser
from app import socketio, mqtt, db, create_mqtt_app
from app.events import bp
from flask_socketio import emit, send
from flask import json
from app.models import User, Sensor
from datetime import datetime

ctx = create_mqtt_app().app_context()

@socketio.on('subscribe')
def handle_subcribe(data):
    if data['topic'] in mqtt.topics.keys():
        pass
    else:
        mqtt.subscribe(str(data['topic']))

@socketio.on('publish')
def handle_publish(data):
    mqtt.publish(data['topic'], data['status'])

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    with ctx:
        user = User.query.filter_by(mqtt_topic=message.topic).first()
        data = json.loads(message.payload.decode())
        sensor_value = json.dumps(data)
        sensor = Sensor(sensor_value=data) #sensor_value field need json object not json string
        sensor.sensor_time = datetime.utcnow()
        user.sensors.append(sensor)
        db.session.add(user)
        db.session.commit()
    data = dict(
        topic=message.topic,
        payload=sensor_value
    )
    socketio.emit(message.topic, data=data)