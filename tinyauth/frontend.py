import datetime
import json
import uuid
from urllib.parse import urljoin, urlparse

import jwt
from flask import (
    Blueprint,
    Response,
    abort,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
)
from flask_restful import reqparse

from tinyauth.models import User

frontend_blueprint = Blueprint('frontend', __name__, static_folder=None)

user_parser = reqparse.RequestParser()
user_parser.add_argument('username', type=str, location='json', required=True)
user_parser.add_argument('password', type=str, location='json', required=True)


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def get_session():
    session = request.cookies.get('tinysess')

    if not session:
        return None

    try:
        token = jwt.decode(session, current_app.config['SECRET_SIGNING_KEY'])
    except jwt.InvalidTokenError:
        return None

    return token


@frontend_blueprint.route('/login/static/<path:path>')
def login_static(path):
    return send_from_directory(
        '/app/login-ui/static',
        path,
    )


@frontend_blueprint.route('/logout')
def logout():
    response = redirect('/login')

    if 'tinysess' in request.cookies:
        response.set_cookie('tinysess', '', expires=0)

    if 'tinycsrf' in request.cookies:
        response.set_cookie('tinycsrf', '', expires=0)

    return response


@frontend_blueprint.route('/login')
def login():
    if get_session():
        return redirect('/')

    if current_app.config.get('DEBUG', True):
        assets = {
           'main.js': 'static/js/bundle.js',
        }
    else:
        with open('/app/login-ui/asset-manifest.json', 'r') as fp:
            assets = json.loads(fp.read())

    return render_template(
       'frontend/login.html',
       js_hash='login/' + assets['main.js'],
      )


@frontend_blueprint.route('/login', methods=["POST"])
def login_post():
    if get_session():
        return redirect('/')

    req = user_parser.parse_args()

    user = User.query.filter(User.username == req['username']).first()
    if not user or not user.password:
        return Response('', 401)

    if not user.is_valid_password(req['password']):
        return Response('', 401)

    expires = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    csrf_token = str(uuid.uuid4())

    jwt_token = jwt.encode({
        'user': user.id,
        'mfa': False,
        'exp': expires,
        'iat': datetime.datetime.utcnow(),
        'csrf-token': csrf_token,
    }, current_app.config['SECRET_SIGNING_KEY'], algorithm='HS256')

    response = jsonify({})
    response.set_cookie('tinysess', jwt_token, httponly=True, secure=True, expires=expires)
    response.set_cookie('tinycsrf', csrf_token, httponly=False, secure=True, expires=expires)

    return response


@frontend_blueprint.route('/static/<path:path>')
def static(path):
    session = get_session()
    if not session:
        abort(404)

    return send_from_directory(
        '/app/admin-ui/static',
        path,
    )


@frontend_blueprint.route('/')
def index():
    session = get_session()
    if not session:
        return redirect('/login')

    if current_app.config.get('DEBUG', True):
        assets = {
           'main.js': 'static/js/bundle.js',
           'main.css': 'static/css/main.css',
        }
    else:
        with open('/app/admin-ui/asset-manifest.json', 'r') as fp:
            assets = json.loads(fp.read())

    return render_template(
       'frontend/index.html',
       css_hash=assets['main.css'],
       js_hash=assets['main.js'],
    )
