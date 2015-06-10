# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import Blueprint, g, render_template
from flask.ext.login import login_required, current_user
from app.models import User, Post
# from .. import db

blog = Blueprint('blog', __name__, template_folder='templates')


@blog.route('/')
@blog.route('/index')
@login_required
def index():
    return render_template('blog/index.html')
