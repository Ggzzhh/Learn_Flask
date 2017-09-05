# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# flask拓展 flask-wtf
from flask_wtf import FlaskForm, Form
# stringField 就是type=text的input  submit同理
from wtforms import StringField, SubmitField, PasswordField, BooleanField
# 导入验证器 的要求
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


# 注册表单
class RegistrationFrom(Form):
    email = StringField("邮箱：", validators=[DataRequired(), Length(1, 64),
                                           Email()])
    username = StringField("用户名：", validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$',
                                              0, "大小写字母开头且只能包含"
                                                 "数字字母下划线以及.（6-16位）")])
    password = PasswordField('密码：', validators=[DataRequired(), EqualTo(
        'password2', message='两次输入的密码必须一致！')])
    password2 = PasswordField('请再次输入密码：', validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已经注册！')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已经被使用！')

# 创建一个登录表单类
class LoginForm(FlaskForm):
    email = StringField('邮箱：', validators=[DataRequired(), Length(1, 64),
                                           Email()])
    password = PasswordField('密码：', validators=[DataRequired()])
    remember_me = BooleanField('记住我！')
    submit = SubmitField('登 录')
