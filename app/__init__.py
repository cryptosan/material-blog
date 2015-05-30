# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.bcrypt import Bcrypt
from config import basedir


app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'


from app import views, models
