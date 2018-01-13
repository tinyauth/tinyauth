#! /usr/bin/env python3

import logging
import os

import click
from flask import Flask
from flask.cli import FlaskGroup
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.contrib.fixers import ProxyFix

db = SQLAlchemy()


def create_app(info):
    app = Flask(
        __name__,
        static_folder=None,
    )

    app.wsgi_app = ProxyFix(app.wsgi_app)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///app.db')
    app.config['BUNDLE_ERRORS'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)

    CORS(app, resources={r'/api/*': {'origins': '*', 'expose_headers': 'Content-Range'}})

    from . import resources
    app.register_blueprint(resources.user_blueprint)
    app.register_blueprint(resources.access_key_blueprint)
    app.register_blueprint(resources.user_policy_blueprint)
    app.register_blueprint(resources.group_blueprint)
    app.register_blueprint(resources.group_policy_blueprint)
    app.register_blueprint(resources.service_blueprint)

    from . import frontend
    app.register_blueprint(frontend.frontend_blueprint)

    Migrate(app, db)

    return app


@click.group(cls=FlaskGroup, create_app=create_app)
def cli():
    """This is a management script for the wiki application."""


@cli.command()
def createdevuser():
    from .models import AccessKey, User, UserPolicy, db
    p = UserPolicy(name='root', policy={'Statement': [{'Action': '*', 'Resource': '*', 'Effect': 'Allow'}]})
    db.session.add(p)

    u = User(username='root')
    u.set_password('password')
    u.policies.append(p)
    db.session.add(u)

    k = AccessKey(access_key_id='gatekeeper', secret_access_key='keymaster', user=u)
    db.session.add(k)

    db.session.commit()

    click.echo("'root' account created")
