from microauth.app import db


user_policies = db.Table('user_policies',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('policy_id', db.Integer, db.ForeignKey('policy.id'), primary_key=True)
)


class Policy(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    policy = db.JSON()

    def __repr__(self):
        return f'<Policy {self.self.name!r}>'


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128))

    policies = db.relationship(
        'Policy',
        secondary=user_policies,
        lazy='subquery',
        backref=db.backref('policies', lazy=True)
    )

    def __repr__(self):
        return f'<User {self.username!r}>'
