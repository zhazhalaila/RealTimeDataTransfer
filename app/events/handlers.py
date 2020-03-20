import functools
from app import socketio, mqtt, db
from app.events import bp
from flask_socketio import emit, send

@socketio.on('subscribe')
def handle_subcribe(data):
    mqtt.subscribe(str(data['topic']))
    print(mqtt.topics)
    print(db)

@socketio.on('unsubscribe')
def handle_unsubscribe(data):
    mqtt.unsubscribe(str(data['topic']))
    print(mqtt.topics)

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    print(db)
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    socketio.emit(message.topic, data=data)