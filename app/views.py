# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from app import app, db, lm
from .models import User
from .forms import LoginForm
from flask import render_template, redirect, flash, redirect, session, \
    url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, \
    login_required


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def before_request():
    """Provider object of the logged in user to g object, all requests
    will have access to the logged in user.

    current_user global is set by Flask-Login, so to set the g object that
    the object can share on app life cycle.
    """
    g.user = current_user


@app.route('/')
@app.route('/index')
@login_required
def index():
    """View index page, when a user is logged in."""
    # Fake datas for unittest.
    user = {
        'nickname': 'Cryptos'
    }
    posts = [
        {
            'author': {'nickname': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'nickname': 'Cryptos'},
            'body': 'The weather is so hot now!!'
        }
    ]

    return render_template('index.html',
                           title='Home',
                           user=user,
                           posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Log a user in."""
    # When a user is already loged in, return to index page.
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('Invalid login. Please try again.')
            redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
    return render_template('login.html',
                           title='Sign in',
                           form=form,
                           providers=app.config['OPENID_PROVIDERS'])


# @oid.after_login
# def after_login(resp):
#     """Check the datas before log in, and Log a user in.

#     :param resp: A dictionary has information returned by the OpenID provider.
#     :type resp: dictionary
#     """
#     # Check the email data from resp,
#     # and if there is no data, return to login page.
#     if resp.email is None or resp.email == "":
#         flash('Invalid login. Please try again.')
#         return redirect(url_for('login'))

#     # Check a user data from Database.
#     user = User.query.filter_by(email=resp.email).first()
#     if user is None:
#         nickname = resp.nickname
#         if nickname is None or nickname == "":
#             nickname = resp.email.split('@')[0]
#         user = User(nickname=nickname, email=resp.email)
#         db.session.add(User)
#         db.session.commit()

#     remember_me = False
#     if 'remember_me' in session:
#         remember_me = session['remember_me']
#         session.pop('remember_me', None)

#     # When all datas are validated, logs a user in.
#     login_user(user, remember=remember_me)
#     return redirect(request.args.get('next') or url_for('index'))
