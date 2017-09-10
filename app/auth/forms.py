# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# flask拓展 flask-wtf
from flask_wtf import FlaskForm
# stringField 就是type=text的input  submit同理
from wtforms import StringField, SubmitField, PasswordField, BooleanField
# 导入验证器 的要求
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


# 注册表单
class RegistrationFrom(FlaskForm):
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


class ResetForm(FlaskForm):
    """重置密码表单"""
    email = StringField("邮箱", validators=[DataRequired(), Length(1, 64),
                                          Email()])
    submit = SubmitField('确定')
    

class ResetFormRequest(FlaskForm):
    """重置密码表单 修改"""
    password = PasswordField("新密码：", validators=[DataRequired(), EqualTo(
        'password2', message="两次密码不一致！")])
    password2 = PasswordField("请再次输入新密码：", validators=[DataRequired()])
    submit = SubmitField("确定!")
    
    
class ChangePasswordForm(FlaskForm):
    """修改密码表单"""
    old_password = PasswordField("旧密码：", validators=[DataRequired()])
    password = PasswordField("新密码：", validators=[DataRequired(), EqualTo(
        'password2', message="两次密码不一致！")])
    password2 = PasswordField("请再次输入新密码：", validators=[DataRequired()])
    submit = SubmitField("确定!")
    
    
class ChangeEmailForm(FlaskForm):
    """修改登录邮箱"""
    password = PasswordField("请输入密码：", validators=[DataRequired()])
    new_email = StringField("新邮箱地址",
                            validators=[DataRequired(),Length(1, 64), Email()])
    submit = SubmitField("确定!")
    
    def validate_new_email(self, field):
        """当函数以validate_打头时， 检查字段时候会一起调用本函数"""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("该邮箱已经被注册！")
    