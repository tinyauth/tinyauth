#! /usr/bin/env python3

import logging
import os

import click
from flask import Flask
from flask.cli import FlaskGroup

from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app(info):
    app = Flask(__name__)
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
    app.register_blueprint(resources.group_blueprint)
    app.register_blueprint(resources.service_blueprint)
        
    api = Api(app, prefix='/api/v1')

    migrate = Migrate(app, db)

    return app


@click.group(cls=FlaskGroup, create_app=create_app)
def cli():
    """This is a management script for the wiki application."""


@cli.command()
def createdevuser():
    from .models import AccessKey, User, Policy, db
    p = Policy(name='root', policy={'Statement': [{'Action': '*', 'Resource': '*', 'Effect': 'Allow'}]})
    db.session.add(p)

    u = User(username='root')
    u.policies.append(p)
    db.session.add(u)

    k = AccessKey(access_key_id='gatekeeper', secret_access_key='keymaster', user=u)
    db.session.add(k)

    db.session.commit()

    click.echo("'root' account created")
