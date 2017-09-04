# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# flask拓展 flask-wtf
from flask_wtf import FlaskForm
# stringField 就是type=text的input  submit同理
from wtforms import StringField, SubmitField, PasswordField, BooleanField
# 导入验证器 的要求
from wtforms.validators import DataRequired, Length, Email

# 创建一个表单类
class LoginForm(FlaskForm):
    email = StringField('邮箱：', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    password = PasswordField('密码：', validators=[DataRequired()])
    remember_me = BooleanField('记住我！')
    submit = SubmitField('登 录')