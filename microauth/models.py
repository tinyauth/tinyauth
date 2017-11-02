import json

import sqlalchemy.types as types

from microauth.app import db


class StringyJSON(types.TypeDecorator):
    """Stores and retrieves JSON as TEXT."""

    impl = types.TEXT

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


# TypeEngine.with_variant says "use StringyJSON instead when
# connecting to 'sqlite'"
MagicJSON = types.JSON().with_variant(StringyJSON, 'sqlite')

user_policies = db.Table(
    'user_policies',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('policy_id', db.Integer, db.ForeignKey('policy.id'), primary_key=True)
)

group_policies = db.Table(
    'group_policies',
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True),
    db.Column('policy_id', db.Integer, db.ForeignKey('policy.id'), primary_key=True)
)

group_users = db.Table(
    'group_users',
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)


class Group(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))

    policies = db.relationship(
        'Policy',
        secondary=group_policies,
        lazy='subquery',
        backref=db.backref('policies', lazy=True)
    )

    def __repr__(self):
        return f'<Group {self.name!r}>'


class Policy(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    policy = db.Column(MagicJSON)

    def __repr__(self):
        return f'<Policy {self.name!r}>'


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128))

    groups = db.relationship(
        'Group',
        secondary=group_users,
        lazy='subquery',
        backref=db.backref('users', lazy=True)
    )

    policies = db.relationship(
        'Policy',
        secondary=user_policies,
        lazy='subquery',
        backref=db.backref('users', lazy=True)
    )

    access_keys = db.relationship('AccessKey', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username!r}>'


class AccessKey(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    access_key_id = db.Column(db.String(128))
    secret_access_key = db.Column(db.String(128))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<AccessKey {self.access_key_id!r}>'
