import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    FLASK_ADMIN_SWATCH = 'cerulean'
    # MySQL config
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql://root:password@127.0.0.1:3306/graduate'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Redis config
    CACHE_TYPE = 'redis'
    CACHE_REDIS_HOST = '127.0.0.1'
    CACHE_REDIS_PORT = '6379'
    CACHE_REDIS_URL = 'redis://127.0.0.1:6379'