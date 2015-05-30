# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from app import db, bcrypt


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    pw_hash = db.Column(db.String(128))
    email = db.Column(db.String(128), index=True, unique=True)
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)		# python 2
        except NameError:
            return str(self.id)			# python 3

    def check_password(hashed_password, password):
        return bcrypt.check_password_hash(hashed_password, password)

    def make_a_hash(password):
        return bcrypt.generate_password_hash(password)

    def __repr__(self):
        return '<User {0}>'.format(self.nickname)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {0}>'.format(self.body)
