#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# flask拓展 flask-wtf
from flask_wtf import FlaskForm
# stringField 就是type=text的input  submit同理
from wtforms import StringField, SubmitField, TextAreaField, \
    BooleanField, SelectField
# 导入验证器 的要求
from wtforms.validators import DataRequired, Length, Email, Regexp


class EditProfileForm(FlaskForm):
    """用户级别的资料编辑表单"""
    name = StringField("个人姓名：", validators=[Length(0, 64)])
    location = StringField("所在地：", validators=[Length(0, 64)])
    about_me = TextAreaField("个人介绍")
    submit = SubmitField("确定!")


class EditProfileAdminForm(FlaskForm):
    """管理员级别的资料编辑表单"""
    email = StringField("邮箱：", validators=[DataRequired(), Length(1, 64),
                                           Email()])
    username = StringField("用户名：", validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$',
                                              0, "大小写字母开头且只能包含"
                                                 "数字字母下划线以及.（6-16位）")])
    confirmed = BooleanField("认证")
    role = SelectField('Role', coerce=int)
    name = StringField("个人姓名：", validators=[Length(0, 64)])
    location = StringField("所在地：", validators=[Length(0, 64)])
    about_me = TextAreaField("个人介绍")
    submit = SubmitField("确定!")