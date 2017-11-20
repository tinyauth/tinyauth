import json

from flask import Blueprint, render_template, send_from_directory

frontend_blueprint = Blueprint('frontend', __name__, static_folder=None)


@frontend_blueprint.route('/static/<path:path>')
def static(path):
    return send_from_directory(
        '/app/react/static',
        path,
    )


@frontend_blueprint.route('/')
def index():
    with open('/app/react/asset-manifest.json', 'r') as fp:
        assets = json.loads(fp.read())

    return render_template(
       'frontend/index.html',
       css_hash=assets['main.css'],
       js_hash=assets['main.js'],
      )
