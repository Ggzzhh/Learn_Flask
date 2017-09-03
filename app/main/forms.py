#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# flask拓展 flask-wtf
from flask_wtf import FlaskForm
# stringField 就是type=text的input  submit同理
from wtforms import StringField, SubmitField
# 导入验证器 的要求
from wtforms.validators import DataRequired

# 创建一个表单类
class NameForm(FlaskForm):
    name = StringField('你的名字是？', validators=[DataRequired()])
    submit = SubmitField('submit')