import json

from flask import Blueprint, render_template


frontend_blueprint = Blueprint('frontend', __name__)


@frontend_blueprint.route('/')
def index():
    with open('/app/react/asset-manifest.json', 'r') as fp:
        assets = json.loads(fp.read())

    return render_template(
       'frontend/index.html',
       css_hash=assets['main.css'],
       js_hash=assets['main.js'],
      )
