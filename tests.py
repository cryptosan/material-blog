# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
from app import app, db
from app.models import User


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
        assert u1.followed.count() is 1
        assert u1.followed.first().nickname == 'foll2'
        assert u2.followers.count() is 1
        assert u2.followers.first().nickname == 'foll1'
        u = u1.unfollow(u2)
        assert u is not None
        db.session.add(u)
        db.session.commit()
        assert not u1.is_following(u2)
        assert u1.followed.count() is 0
        assert u2.followers.count() is 0

if __name__ == '__main__':
    unittest.main()
