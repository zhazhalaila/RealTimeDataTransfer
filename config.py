import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    FLASK_ADMIN_SWATCH = 'cerulean'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql://root:password@127.0.0.1:3306/graduate'
    SQLALCHEMY_TRACK_MODIFICATIONS = False