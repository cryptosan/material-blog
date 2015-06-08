# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

# Setting funcs.
REGISTER_ENABLED = False
POST_PER_PAGE = 3
WTF_CSRF_ENABLED = True
SECRET_KEY = 'youdontknowthis$'
# Full text search engine path.
WHOOSH_BASE = os.path.join(basedir, 'search.db')
MAX_SEARCH_RESULTS = 25

# Theme list.
THEME_LIST = {
    'Default': 'default'
}

# Setting for using theme.
USE_THEME = 'Default'

# Setting paths of static, and templates folder
STATIC_PATH = os.path.join('themes', THEME_LIST[USE_THEME], 'static')
TEMPLATES_PATH = os.path.join('themes', THEME_LIST[USE_THEME], 'templates')
