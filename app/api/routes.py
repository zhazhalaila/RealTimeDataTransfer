from flask import jsonify
from app.models import User, Sensor
from app.api import bp

@bp.route('/user/<username>')
def user_api(username):
    user = User.query.filter_by(username=username).first()
    #last 24 hours sensor value
    sensors = user.sensors.order_by(Sensor.sensor_time.desc()).limit(24)
    sensors_list = list(map(lambda sensor : sensor.to_dict(), sensors))
    return jsonify(sensors_list)