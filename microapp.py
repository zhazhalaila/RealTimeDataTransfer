from app import create_app, db, cli, socketio
from app.models import User, Sensor

app = create_app()
cli.register(app)

@app.shell_context_processor
def make_shell_context():
    return {'db':db, 'User': User, 'Sensor': Sensor}

if __name__ == '__main__':
    #support https
    socketio.run(app, async_mode=async_mode,cors_allowed_origins="*")