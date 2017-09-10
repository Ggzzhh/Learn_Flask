#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from . import login_manager

# flask要求用户实现一个回调函数 返回用户对象或者None
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 创建数据库表
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')
    
    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    # 加入密码散列
    password_hash = db.Column(db.String(128))
    # 在数据库中插入验证状态一栏
    confirmed = db.Column(db.Boolean, default=False)

    # 对密码进行属性化并加密
    @property
    def password(self):
        raise AttributeError('密码不是一个可读属性！')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # 解码密码并进行验证 返回布尔值
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self):
        """生成验证标记"""
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=3600)
        return s.dumps({'confirm': self.id})

    @staticmethod
    def my_get_id(token):
        """解码token获取用户id"""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return data.get('confirm')
        

    def confirm(self, token):
        """验证邮箱"""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
        # data = self.get_id(token)
        # if data != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True
    
    def change_email(self, token):
        """更改邮箱"""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        self.email = data.get('email')
        db.session.add(self)
        return True
    
    def generate_email_change_token(self, email=None):
        """生产邮箱更改使用的令牌"""
        if email is None:
            email = self.email
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'email': email})
    

    def __repr__(self):
        return '<User %r>' % self.username