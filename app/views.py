# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from app import app, lm
from app.models import User
from flask import render_template, redirect, flash
from .forms import LoginForm


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/')
@app.route('/index')
def index():
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
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for openID="%s", remember_me=%s' %
              (form.openid.data, str(form.remember_me.data)))
        return redirect('/index')
    return render_template('login.html',
                           title='Sign in',
                           form=form,
                           providers=app.config['OPENID_PROVIDERS'])
