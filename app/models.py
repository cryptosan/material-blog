# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from app import app, db, bcrypt
from hashlib import md5

# Doesn't work on Python 3.
import flask.ext.whooshalchemy as whooshalchemy


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    pw_hash = db.Column(db.String(128))
    email = db.Column(db.String(128), index=True, unique=True)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)
    followed = db.relationship(
        'User',
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % \
            (md5(self.email.encode('utf-8')).hexdigest(), size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id). \
            count() > 0

    def followed_posts(self):
        return Post.query.join(followers, (
            followers.c.followed_id == Post.user_id)). \
            filter(followers.c.follower_id == self.id). \
            order_by(Post.timestamp.desc())

    def get_id(self):
        try:
            return unicode(self.id)     # python 2
        except NameError:
            return str(self.id)         # python 3

    def check_password(self, password):
        return bcrypt.check_password_hash(self.pw_hash, password)

    def make_a_hash(self, password):
        self.pw_hash = bcrypt.generate_password_hash(password)

    def __repr__(self):
        return '<User {0}>'.format(self.nickname)


class Post(db.Model):
    __searchable__ = ['body']

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {0}>'.format(self.body)


# Run whooshalchemy.
whooshalchemy.whoosh_index(app, Post)
