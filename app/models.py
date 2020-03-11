import pickle
from hashlib import md5
from app import db, login, cache
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    mqtt_topic = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    #one to many
    sensors = db.relationship('Sensor', backref='owner', lazy='dynamic')
    #many to many
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_sensors(self):
        return Sensor.query.join(
            followers, (followers.c.followed_id == Sensor.user_id)).filter(
                followers.c.follower_id == self.id)

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
    db.session.add(use_obj)
    return use_obj

class Sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensorname = db.Column(db.String(30))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Sensor {}>'.format(self.sensorname)