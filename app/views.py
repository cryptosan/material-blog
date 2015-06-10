# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from app import app, db, lm, signup
from config import POST_PER_PAGE, MAX_SEARCH_RESULTS
from .models import User, Post
from .forms import LoginForm, RegisterForm, EditForm, PostForm, SearchForm, \
    EditPostForm
from flask import render_template, redirect, flash, redirect, session, \
    url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, \
    login_required
from flask.ext.register import register_required
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
    g.register_form = signup.is_enabled()
    g.user = current_user
    if g.user.is_authenticated():
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()
        g.search_form = SearchForm()


@app.route('/')
@app.route('/index')
def index():
    """View index page"""
    config = {
        'jumbotron': {
            'header': 'Material Blog',
            'desc': 'This is a simple material blog for portfolio.',
            'link': '#'
        }
    }
    return render_template('index.html',
                           title='Home',
                           conf=config)


@app.route('/timeline', methods=['GET', 'POST'])
@app.route('/timeline/<int:page>', methods=['GET', 'POST'])
@login_required
def timeline(page=1):
    """View timeline page"""
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data,
                    timestamp=datetime.utcnow(),
                    author=g.user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('timeline'))
    posts = g.user.followed_posts().paginate(page, POST_PER_PAGE, False)
    return render_template('timeline.html',
                           title='Timeline',
                           form=form,
                           posts=posts)


@app.route('/user/<nickname>', methods=['GET', 'POST'])
@app.route('/user/<nickname>/<int:page>', methods=['GET', 'POST'])
@login_required
def user(nickname, page=1):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User {0} not found.'.format(nickname))
        return redirect(url_for('index'))
    editpost = EditPostForm()
    if editpost.validate_on_submit():
        post = user.posts.filter_by(id=editpost.post_id.data).first()
        post.body = editpost.post.data
        db.session.add(post)
        db.session.commit()
        flash('The post was edited!')
        return redirect(url_for('user', nickname=g.user.nickname))
    posts = user.posts.order_by(Post.timestamp.desc()). \
        paginate(page, POST_PER_PAGE, False)
    return render_template('user.html',
                           title='Profile',
                           user=user,
                           posts=posts,
                           editpostform=editpost)


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    """Edit a user profile that be requested."""
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html', title='Edit', form=form)


@app.route('/delete/<int:post_id>')
@login_required
def delete(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if post is None:
        flash('Post not found!')
        return redirect(url_for('timeline', nickname=g.user.nickname,
                                alert='danger'))
    if g.user.id is not post.user_id:
        flash('You\'re not a owner.!')
        return redirect(url_for('timeline', nickname=g.user.nickname,
                                alert='danger'))
    db.session.delete(post)
    db.session.commit()
    flash('The post has just deleted!')
    return redirect(url_for('user', nickname=g.user.nickname))


@app.route('/search', methods=['POST'])
@login_required
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('index'))
    return redirect(url_for('search_results', query=g.search_form.search.data))


@app.route('/search_results/<query>')
@login_required
def search_results(query):
    # results = Post.query.whoosh_search(Post.body.contains(query),
    #                                    MAX_SEARCH_RESULTS).all()
    results = Post.query.filter(Post.body.contains(query)).all()
    return render_template('search_results.html',
                           query=query,
                           results=results)


@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User {0} not found.'.format(nickname))
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t follow yourself!')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.follow(user)
    if u is None:
        flash('You are already following {0}'.format(nickname))
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You are now following {0}!'.format(nickname))
    return redirect(url_for('user', nickname=nickname))


@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User {0} not found.'.format(nickname))
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t unfollow yourself!')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.unfollow(user)
    if u is None:
        flash('You already unfollowed {0}!'.format(nickname))
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You don\'t follow {0} anymore'.format(nickname))
    return redirect(url_for('user', nickname=nickname))


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
        return redirect(url_for('timeline'))
    return render_template('login.html',
                           title='Sign in',
                           form=form)


@app.route('/logout')
def logout():
    """Log a user out"""
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
@register_required
def register():
    """Sign a user up."""
    # When a user is already logged in, return to index page.
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
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
    return render_template('404.html', title='404'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html', title='500'), 500
