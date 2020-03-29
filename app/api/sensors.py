from flask import jsonify, request
from app.models import User, Sensor
from app.api import bp

# return sensors list value of json format
@bp.route('/sensor/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = Sensor.to_collection_dict(Sensor.query, page, per_page, 'api.user', username=username)
    return jsonify(data)

@bp.route('/user/<username>')
def user_api(username):
    user = User.query.filter_by(username=username).first()
    #last 24 hours sensor value
    sensors = user.sensors.order_by(Sensor.sensor_time.desc()).limit(24)
    sensors_list = list(map(lambda sensor : sensor.to_dict(), sensors))
    return jsonify(sensors_list)