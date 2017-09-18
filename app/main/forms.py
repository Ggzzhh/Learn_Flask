#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# flask拓展 flask-wtf
from flask_wtf import FlaskForm
# stringField 就是type=text的input  submit同理
from wtforms import StringField, SubmitField, TextAreaField, \
    BooleanField, SelectField
# 导入验证器 的要求
from wtforms.validators import DataRequired, Length, \
    Email, Regexp, ValidationError
from ..models import Role, User
# 导入富文本编辑框
from flask_pagedown.fields import PageDownField


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

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in
                             Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        """验证email是否被修改且修改后是否被注册，提交表单时验证"""
        if field.date != self.user.email and \
                User.query.filter_by(email=field.date).first():
            raise ValidationError('邮箱已经被注册！')

    def validate_username(self, field):
        """验证修改后的用户名是否被注册"""
        if field.date != self.user.username and \
                User.query.filter_by(username=field.date).first():
            raise ValidationError('用户名已经被注册！')


class PostForm(FlaskForm):
    """博客文章表单"""
    body = PageDownField("发微博", validators=[DataRequired()],
                         render_kw={"rows": 3})
    submit = SubmitField("提交")


class CommentForm(FlaskForm):
    """评论用表单"""
    body = PageDownField('输入你的评论', validators=[DataRequired()])
    submit = SubmitField('提交')
