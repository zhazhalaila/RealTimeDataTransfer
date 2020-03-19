import functools
from app import socketio, mqtt
from app.events import bp
from flask_socketio import emit, send

@socketio.on('subscribe')
def handle_subcribe(data):
    mqtt.subscribe(str(data['topic']))

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    socketio.emit(message.topic, data=data)