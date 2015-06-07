# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
from app import app, db
from app.models import User
from datetime import datetime, timedelta
from app.models import User, Post


class TestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        # unittest in memory
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_avatar(self):
        u = User(nickname='john', email='john@example.com')
        avatar = u.avatar(128)
        expected = 'http://www.gravatar.com/avatar/' \
            'd4c74594d841139328695756648b6bd6'
        assert avatar[0:len(expected)] == expected

    def test_password_hash(self):
        u = User(nickname='pass', email='pass@pass.com')
        u.make_a_hash('passwordofpass')
        assert u.check_password('passwordofpass')

    def test_follow(self):
        u1 = User(nickname='foll1', email='foll1@example.com')
        u2 = User(nickname='foll2', email='foll2@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        assert u1.unfollow(u2) is None
        u = u1.follow(u2)
        db.session.add(u)
        db.session.commit()
        assert u1.follow(u2) is None
        assert u1.is_following(u2)
        assert u1.followed.count() == 1
        assert u1.followed.first().nickname == 'foll2'
        assert u2.followers.count() == 1
        assert u2.followers.first().nickname == 'foll1'
        u = u1.unfollow(u2)
        assert u is not None
        db.session.add(u)
        db.session.commit()
        assert not u1.is_following(u2)
        assert u1.followed.count() == 0
        assert u2.followers.count() == 0

    def test_follow_posts(self):
        # make four users
        u1 = User(nickname='john', email='john@example.com')
        u2 = User(nickname='susan', email='susan@example.com')
        u3 = User(nickname='mary', email='mary@example.com')
        u4 = User(nickname='david', email='david@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.add(u4)
        # make four posts
        utcnow = datetime.utcnow()
        p1 = Post(body='post from john', author=u1,
                  timestamp=utcnow + timedelta(seconds=1))
        p2 = Post(body='post from susan', author=u2,
                  timestamp=utcnow + timedelta(seconds=2))
        p3 = Post(body='post from mary', author=u3,
                  timestamp=utcnow + timedelta(seconds=3))
        p4 = Post(body='post from david', author=u4,
                  timestamp=utcnow + timedelta(seconds=4))
        db.session.add(p1)
        db.session.add(p2)
        db.session.add(p3)
        db.session.add(p4)
        db.session.commit()
        # setup the followers
        u1.follow(u1)   # john follows himself
        u1.follow(u2)   # john follows susan
        u1.follow(u4)   # john follows david
        u2.follow(u2)   # susan follows herself
        u2.follow(u3)   # susan follows mary
        u3.follow(u3)   # mary follows herself
        u3.follow(u4)   # mary follows david
        u4.follow(u4)   # david follows himself
        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.add(u4)
        db.session.commit()
        # check the followed posts of each user
        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        assert len(f1) == 3
        assert len(f2) == 2
        assert len(f3) == 2
        assert len(f4) == 1
        assert f1 == [p4, p2, p1]
        assert f2 == [p3, p2]
        assert f3 == [p4, p3]
        assert f4 == [p4]

if __name__ == '__main__':
    unittest.main()
