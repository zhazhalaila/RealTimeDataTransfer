from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    sensors = db.relationship('Sensor', backref='owner', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensorname = db.Column(db.String(30))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Sensor {}>'.format(self.sensorname)