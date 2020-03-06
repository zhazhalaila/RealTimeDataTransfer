from flask import Flask
from flask_admin import Admin
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
admin = Admin(app, name='microblog', template_mode='bootstrap3')

from app import routes