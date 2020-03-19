from app import socketio
from flask_socketio import emit, send

@socketio.on('my event')
def handle_my_custom_event(json):
    emit('server message', json);