#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from datetime import datetime
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from . import login_manager


# flask要求用户实现一个回调函数 返回用户对象或者None
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# 要支持的用户角色以及定义角色的使用权限
class Permission:
    FOLLOW = 0x01   # 关注其他用户
    COMMENT = 0x02  # 在他人写的文章中发布评论
    WRITE_ARTICLES = 0x04   # 写自己的原创文章
    MODERATE_COMMENTS = 0x08  # 查处他人发布的不当评论
    ADMINISTER = 0x80  # 管理网站，管理员


# 创建数据库表
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer) # 表明用户权限
    users = db.relationship('User', backref='role', lazy='dynamic')

    # 手动添加容易出错 所以用方法添加角色
    @staticmethod
    def insert_roles():
        roles = {
            "User": (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            "Moderator": (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES|
                          Permission.MODERATE_COMMENTS, False),
            "Administrator": (0xff, True)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()
    
    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    """用户相关数据库的创建以及各种数据库操作"""
    # 构造函数调用基类的构造函数完成用户创建
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    # 加入密码散列
    password_hash = db.Column(db.String(128))
    # 在数据库中插入验证状态一栏
    confirmed = db.Column(db.Boolean, default=False)
    # 用户资料
    name = db.Column(db.String(64))  # 姓名
    location = db.Column(db.String(64))  # 所在地
    about_me = db.Column(db.Text())  # 自我介绍
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)  # 注册时间
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)  # 最后登录时间

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

    def can(self, permissions):
        """检查用户是否有指定权限"""
        return self.role is not None and (self.role.permissions &
                                          permissions) == permissions

    def is_administrator(self):
        """检查用户是否是管理员"""
        return self.can(Permission.ADMINISTER)

    def ping(self):
        """刷新用户访问时间"""
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    """游客（匿名用户）专用类"""

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False