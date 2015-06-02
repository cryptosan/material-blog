# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask.ext.wtf import Form
from wtforms import PasswordField, StringField, SubmitField, BooleanField, \
    TextAreaField, ValidationError
from wtforms.validators import Email, DataRequired, Length, EqualTo, \
    Required, Regexp
from .models import User


class LoginForm(Form):
    email = StringField('Email', [
        DataRequired(),
        Length(1, 64),
        Email('It\'s not an Email!')
    ])
    password = PasswordField('Password', [DataRequired()])
    remember_me = BooleanField('remember_me', default=False)
    submit = SubmitField('Submit')


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

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_nickname(self, field):
        if User.query.filter_by(nickname=field.data).first():
            raise ValidationError('Nickname already registered.')


class EditForm(Form):
    nickname = StringField('nickname', validators=[DataRequired()])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])
