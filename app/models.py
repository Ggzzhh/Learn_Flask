#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import hashlib
from datetime import datetime
from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app, request, url_for
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
import bleach
from app.exceptions import ValidationError

from . import login_manager


# flask要求用户实现一个回调函数 返回用户对象或者None
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Comment(db.Model):
    """评论模型"""
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        """当内容改变时， 使用markdown 转换body内容为html"""
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code',
                            'em', 'i', 'strong', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def to_json(self):
        """把评论转换成JSON格式的序列化字典"""
        json_comment = {
            'url': url_for('api.get_comment', id=self.id, _external=True),
            'post': url_for('api.get_post', id=self.post_id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', id=self.author_id, _external=True)
        }
        return json_comment

    @staticmethod
    def from_json(json_comment):
        """通过json数据建立新文章"""
        body = json_comment.get('body')
        if body is None or body == '':
            raise ValidationError('comment does not have a body')
        return Comment(body=body)

db.event.listen(Comment.body, 'set', Comment.on_changed_body)


# 要支持的用户角色以及定义角色的使用权限
class Permission:
    FOLLOW = 0x01   # 关注其他用户
    COMMENT = 0x02  # 在他人写的文章中发布评论
    WRITE_ARTICLES = 0x04   # 写自己的原创文章
    MODERATE_COMMENTS = 0x08  # 查处他人发布的不当评论
    ADMINISTER = 0x80  # 管理网站，管理员


class Post(db.Model):
    """博客文章"""
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body_html = db.Column(db.Text)
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    @staticmethod
    def generate_fake(count=100):
        """生成100条虚拟留言"""
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count-1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                     timestamp=forgery_py.date.date(True),
                     author=u)
            db.session.add(p)
            db.session.commit()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        """
        set事件的监听程序，只要body设置新值，该函数自动被调用
        主要作用是把body字段中的文本渲染成HTML格式，结果在保存在body_html中
        """
        # 允许使用的html标签
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        # 转换过程
        # 1.markdown将文本转换成html
        # 2.bleach.clean 清除掉不符合白名单的标签
        # 3.bleach.linkify 转换文本中类似url以及邮箱为a连接
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def to_json(self):
        json_post = {
            'url': url_for('api.get_post', id=self.id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', id=self.author_id,
                              _external=True),
            'comments': url_for('api.get_post_comments', id=self.id,
                                _external=True),
            'comment_count': self.comments.count()
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if body is None or body == '':
            raise ValidationError('post does not have a body')
        return Post(body=body)

# 监听set事件 只要body设置了新值，就会调用on_changed_body
db.event.listen(Post.body, 'set', Post.on_changed_body)


# 创建数据库表
class Role(db.Model):
    """角色相关"""
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


class Follow(db.Model):
    """关注关联表模型"""
    __tablename__ = "follows"
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(UserMixin, db.Model):
    """用户相关数据库的创建以及各种数据库操作"""

    avatar_hash = db.Column(db.String(32))

    # 构造函数调用基类的构造函数完成用户创建
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = \
                hashlib.md5(self.email.encode('utf-8')).hexdigest()
        self.follow(self)

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
    # 博客相关
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    # 使用两个一对多关系实现多对多关系
    # 用户关注的人
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    # 用户的粉丝
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

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
        self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
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

    def gravatar(self, size=100, default='identicon', rating='g'):
        """使用gravatar生成用户头像"""
        if request.is_secure:  # 如果响应是安全的
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        my_hash = self.avatar_hash or hashlib.md5(self.email.encode(
            'utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=my_hash, size=size, default=default, rating=rating
        )

    # 关注关系的辅助方法
    def follow(self, user):
        """关注某人"""
        # 如果self没有关注user
        if not self.is_following(user):
            # 那么在关系表中添加 关注者是self ，被关注者是user
            # Follow因为外键的关系多出了两个属性
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        """取消关注"""
        # 在self的关注者中查找user
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        """查询是否已关注"""
        # 在self关注的人中查找
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        """查询是否被某人关注"""
        # 在self的粉丝中查找有没有user
        return self.followers.filter_by(follower_id=user.id).first() is not None

    @property
    def followed_posts(self):
        """
        返回联结查询结果： 已关注的用户的文章（包括自己）
        属性化的原因是为了统一格式
        """
        return Post.query.join(Follow, Follow.followed_id == Post.author_id)\
            .filter(Follow.follower_id == self.id)

    @staticmethod
    def generate_fake(count=100):
        """生成虚拟数据 count控制数量"""
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True)
                     )
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            user.follow(user)
            db.session.add(user)
            db.session.commit()

    def to_json(self):
        json_user = {
            'url': url_for('api.get_user', id=self.id, _external=True),
            'username': self.username,
            'member_since': self.member_since,
            'last_seen': self.last_seen,
            'posts': url_for('api.get_user_posts', id=self.id, _external=True),
            'followed_posts': url_for('api.get_user_followed_posts',
                                      id=self.id, _external=True),
            'post_count': self.posts.count()
        }
        return json_user

    def generate_auth_token(self, expiration):
        """生产验证密匙"""
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        """验证密匙 并返回用户id"""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    """游客（匿名用户）专用类"""

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False




