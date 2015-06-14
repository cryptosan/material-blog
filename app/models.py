# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from app import app, db, bcrypt
from hashlib import md5

# Doesn't work on Python 3.
import flask.ext.whooshalchemy as whooshalchemy


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('users.id'))
)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    pw_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), index=True, unique=True, nullable=False)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)
    user_active = db.Column(db.Boolean, default=True, nullable=True)
    followed = db.relationship(
        'User',
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )
    opts = db.relationship("Option", uselist=False, backref="user")

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.user_active

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
    __tablename__ = 'posts'
    __searchable__ = ['body']

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<Post {0}>'.format(self.body)


class Option(db.Model):
    __tablename__ = 'options'

    id = db.Column(db.Integer, primary_key=True)
    blog_state = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<Option {0}>'.format(self.blog_state)

    def is_blog_publishing(self):
        return self.blog_state

    def publish_blog(self, state):
        self.blog_state = state


# Run whooshalchemy.
whooshalchemy.whoosh_index(app, Post)
