#! /usr/bin/env python3

import logging
import os

from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate, MigrateCommand
from flask_restful import Api
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///app.db')

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
app.logger.addHandler(handler)

CORS(app, resources={r'/api/*': {'origins': '*', 'expose_headers': 'Content-Range'}})
api = Api(app, prefix='/api/v1')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)
