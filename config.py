# -*- coding: utf-8 -*-

import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://jeff:cryptos@localhost/mdblog"

# Setting funcs.
REGISTER_ENABLED = True
POST_PER_PAGE = 5
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
