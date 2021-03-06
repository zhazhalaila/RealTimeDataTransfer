import pickle
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, current_app, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from flask_babel import _, get_locale
from werkzeug.urls import url_parse
from app import db, cache
from app.main.forms import SearchForm
from app.models import User, Sensor
from app.main import bp
from flask_cors import cross_origin

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.local = str(get_locale())

@bp.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    sensors = current_user.followed_sensors().paginate(
        page, current_app.config['SENSORS_PER_PAGE'], False)
    next_url = url_for('main.index', page=sensors.next_num) \
        if sensors.has_next else None
    prev_url = url_for('main.index', page=sensors.prev_num) \
        if sensors.has_prev else None
    return render_template('index.html', title='Home', sensors=sensors.items,
                            next_url=next_url, prev_url=prev_url)

@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_('You cannot follow yourself!'))
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_('You are following %(username)s!', username=username))
    return redirect(url_for('main.user', username=username))

@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s.', username=username))
    return redirect(url_for('main.user', username=username))

@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        flash(_('Invalid input'))
        return redirect(url_for('main.index'))
    user = User.query.filter_by(username=g.search_form.q.data).first()
    if user is None:
        flash(_('User %(username)s not found.', username=g.search_form.q.data))
        return redirect(url_for('main.index'))
    else:
        return redirect(url_for('main.user', username=g.search_form.q.data))


@bp.route('/test')
def test():
    user = User.query.get(12)
    return user.username

@bp.route('/cachetest')
def cachetest():
    user = 'user_12'
    use_obj = pickle.loads(cache.get(user)) if cache.get(user) else None
    if use_obj is None:
        query = User.query.get(12)
        use_obj = pickle.dumps(query) #translate query result to bytes
        cache.set(user, use_obj, timeout=180)
        return query.username
    db.session.add(use_obj)
    return use_obj.username