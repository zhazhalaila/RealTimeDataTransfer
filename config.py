import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

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
    # Email config
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['1176694275@qq.com']
    #page config
    SENSORS_PER_PAGE = 25
    #language support
    LANGUAGES = ['zh', 'es']
    #cors config
    CORS_HEADERS = 'Content-Type'
    #Mqtt config
    MQTT_BROKER_URL = 'broker.hivemq.com'
    MQTT_BROKER_PORT = 1883