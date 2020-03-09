import pickle
from app import db, login, cache
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    mqtt_topic = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    sensors = db.relationship('Sensor', backref='owner', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

#use flask-caching and redis
@login.user_loader
def load_user(id):
    user = 'user_{}'.format(id)
    use_obj = pickle.loads(cache.get(user)) if cache.get(user) else None #translate cache result to python object
    if use_obj is None:
        query = User.query.get(int(id))
        use_obj = pickle.dumps(query) #translate query result to bytes
        cache.set(user, use_obj, timeout=3600)
        return query
    return use_obj

class Sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensorname = db.Column(db.String(30))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Sensor {}>'.format(self.sensorname)