from flask import Flask
from flask_caching import Cache
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)
cache = Cache(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
admin = Admin(app, name='microblog', template_mode='bootstrap3')

from app import routes, models

admin.add_view(ModelView(models.User, db.session))
admin.add_view(ModelView(models.Sensor, db.session))