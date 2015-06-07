# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask.ext.wtf import Form
from wtforms import PasswordField, StringField, SubmitField, BooleanField, \
    TextAreaField
from wtforms.validators import Email, DataRequired, Length, EqualTo, \
    Regexp
from .models import User


class LoginForm(Form):
    email = StringField('Email', [
        DataRequired(),
        Length(1, 64),
        Email('It\'s not an Email!')
    ])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)
    submit = SubmitField('Submit')

    def validate(self):
        if not Form.validate(self):
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if user is None:
            self.email.errors.append('Incorrect email!')
            return False
        if not user.check_password(self.password.data):
            self.password.errors.append('Invalid password!')
            return False
        return True


class RegisterForm(Form):
    email = StringField('Email', [
        DataRequired(),
        Email('It\'s not an Email!')
    ])
    nickname = StringField('Nickname', [
        DataRequired(),
        Regexp(
            '^[A-Za-z][A-Za-z0-9_.]*$', 0,
            'Nicknames must have only letters, numbers, dots or underscores'
        ),
        Length(min=4, max=12)
    ])
    password = PasswordField('New Password', [
        DataRequired(),
        EqualTo('confirm', message='Password must match')
    ])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('Register')

    def validate(self):
        if not Form.validate(self):
            return False
        email = User.query.filter_by(email=self.email.data).first()
        if email is not None:
            self.email.errors.append('This email is already in use.')
            return False
        nickname = User.query.filter_by(nickname=self.nickname.data).first()
        if nickname is not None:
            self.nickname.errors.append('This nickname is already in use.')
            return False
        return True


class EditForm(Form):
    nickname = StringField('Nickname', validators=[
        DataRequired(),
        Regexp(
            '^[A-Za-z][A-Za-z0-9_.]*$', 0,
            'Nicknames must have only letters, numbers, dots or underscores'
        ),
        Length(min=4, max=12)
    ])
    about_me = TextAreaField('about_me', validators=[
        Length(min=0, max=140)
    ])

    def __init__(self, original_nickname, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        if not Form.validate(self):
            return False
        if self.nickname.data == self.original_nickname:
            return True
        user = User.query.filter_by(nickname=self.nickname.data).first()
        if user is not None:
            self.nickname.errors.append(
                'This nickname is already in use, Please choose another one.')
            return False
        return True


class PostForm(Form):
    post = StringField('post', validators=[DataRequired()])
