# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from app import app, db, lm
from .models import User
from .forms import LoginForm, RegisterForm
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
    user = g.user
    # Fake datas for unittest.
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


@app.route('/user/<nickname>')
@login_required
def user(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User {0} not found.'.format(nickname))
        return redirect(url_for('index'))
    # Some datas for unittest
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html',
                           user=user,
                           posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Log a user in."""
    # When a user is already logged in, return to index page.
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
                           form=form)


@app.route('/logout')
def logout():
    """Log a user out"""
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Sign a user up."""
    # When a user is already logged in, return to index page.
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))

    form = RegisterForm()
    if form.validate_on_submit():
        # Duplication check for email, and nickname
        form.validate_email(form.email)
        form.validate_nickname(form.nickname)

        user = User(email=form.email.data, nickname=form.nickname.data)
        user.make_a_hash(form.password.data)
        db.session.add(user)
        db.session.commit()
        redirect(url_for('login'))
    return render_template('register.html',
                           title='Sign up',
                           form=form)
