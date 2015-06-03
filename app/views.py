# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from app import app, db, lm
from .models import User
from .forms import LoginForm, RegisterForm, EditForm
from flask import render_template, redirect, flash, redirect, session, \
    url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, \
    login_required
from datetime import datetime


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
    if g.user.is_authenticated():
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()


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
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
    return render_template('login.html',
                           title='Sign in',
                           form=form)


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm()
    if form.validate_on_submit():
        # Check nickname duplication what a user wants.
        if form.nickname.data != g.user.nickname:
            if form.valid_nickname(form.nickname) is not None:
                flash('The nickname is already used!')
                return redirect(url_for('edit'))

        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html', form=form)


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
        if form.valid_email(form.email) is not None:
            flash('The email is already used!')
            return redirect(url_for('register'))
        if form.valid_nickname(form.nickname) is not None:
            flash('The nickname is already used!')
            return redirect(url_for('register'))

        user = User(email=form.email.data, nickname=form.nickname.data)
        user.make_a_hash(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You are registered!')
        return redirect(url_for('login'))
    return render_template('register.html',
                           title='Sign up',
                           form=form)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
