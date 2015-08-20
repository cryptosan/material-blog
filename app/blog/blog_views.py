# -*- coding: utf-8 -*-

from app import db
from config import BLOG_POST_PER_PAGE
from flask import Blueprint, g, render_template, flash, redirect, url_for
from flask.ext.login import login_required, current_user
from .blog_forms import BlogPostForm, BlogEditForm
from app.models import User, BlogPost
from app.forms import SearchForm
from datetime import datetime

blog = Blueprint('blog', __name__, template_folder='templates')


@blog.route('/<int:page>')
@blog.route('/index/<int:page>')
@login_required
def index(page=1):
    """
    Todo
    - 자신이 팔로우 중인 사용자의 블로그 글만 보기.
    - Option 테이블의 blog_state에 따라 자신의 블로그 노출.
    """
    # Print posts all i am following.
#     posts = g.user.followed_blog_posts().paginate(page, POST_PER_PAGE, False)
    posts = g.user.my_blog_posts().paginate(page, BLOG_POST_PER_PAGE, False)
#     posts = g.user.my_blog_posts().all()
    return render_template('blog/index.html',
                           posts=posts)


@blog.route('/post', methods=['GET', 'POST'])
@login_required
def post():
    form = BlogPostForm()
    if form.validate_on_submit():
        post = BlogPost(body=repr(form.blgPostBody.data).strip("'"),
                        subject=form.blgPostSub.data,
                        timestamp=datetime.utcnow(),
                        blog_author=g.user)
        db.session.add(post)
        db.session.commit()
        flash('Your Blog post is now live!')
        return redirect(url_for('blog.index', page=1))
    return render_template('blog/post.html',
                           title='Blog Post',
                           form=form)


@blog.route('/edit/<int:numOfPost>', methods=['GET', 'POST'])
@login_required
def edit(numOfPost):
    blogPost = BlogPost.query.filter_by(id=numOfPost).first()
    if blogPost is None:
        flash('Post not found')
        return redirect(url_for('blog.index', page=1))
    if blogPost.user_id is not g.user.id:
        flash('Not allowed.')
        return redirect(url_for('blog.index', page=1))
    form = BlogEditForm()
    if form.validate_on_submit():
        blogPost = BlogPost.query.filter_by(id=numOfPost).first()
        blogPost.subject = form.blgEditSub.data
        blogPost.body = form.blgEditBody.data
        db.session.add(blogPost)
        db.session.commit()
        flash('Your post was edited!')
        return redirect(url_for('blog.index', page=1))
    else:
        form.blgEditSub.data = blogPost.subject
        form.blgEditBody.data = blogPost.body
        print(repr(blogPost.body))
    return render_template('blog/edit.html',
                           title='Edit Post',
                           form=form)


@blog.route('/delete/<int:numOfPost>')
@login_required
def delete(numOfPost):
    blogPost = BlogPost.query.filter_by(id=numOfPost).first()
    if blogPost is None:
        flash('Post not found')
        return redirect(url_for('blog.index', page=1)) 
    if blogPost.user_id is not g.user.id:
        flash('Not allowed.')
        return redirect(url_for('blog.index', page=1))
    db.session.delete(blogPost)
    db.session.commit()
    flash('The post has just been deleted.')
    return redirect(url_for('blog.index', page=1))

