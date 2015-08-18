# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length
from wsgiref.validate import validator


class BlogPostForm(Form):

    """
    Todo
    - body 필드를 markdown 형식으로 변환.
    """
    blgPostSub = StringField('Subject', validators=[DataRequired(),
                                                  Length(min=0, max=25)])
    blgPostBody = TextAreaField('Body', validators=[DataRequired(),
                                             Length(min=0, max=500)])
    blgPostBtn = SubmitField('Post')
    
    
class BlogEditForm(Form):
    
    """
    Todo
    - 제목/내용 수정.
    """
    blgEditSub = StringField('Subject', validators=[DataRequired(),
                                                Length(min=0, max=25)])
    blgEditBody = TextAreaField('Body', validators=[DataRequired(),
                                            Length(min=0, max=500)])
    blgEditBtn = SubmitField('Edit')
