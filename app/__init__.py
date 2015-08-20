# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.bcrypt import Bcrypt
from flask.ext.register import RegisterManager
from flask.ext.markdown import Markdown


app = Flask(__name__)
app.config.from_object('config')
# Set up paths of templates, and static folder.
app.static_folder = app.config['STATIC_PATH']
app.template_folder = app.config['TEMPLATES_PATH']


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

signup = RegisterManager(app)
signup.save_redirect_view('index')

md = Markdown(app)


# Blueprint
from app.blog import blog
app.register_blueprint(blog, url_prefix='/blog')


if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('tmp/mdblog.log', 'a',
                                       1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('material blog startup')


from app import views, models
