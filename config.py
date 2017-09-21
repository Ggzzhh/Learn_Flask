#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
basedir = os.path.abspath(os.path.dirname(__file__))


# 基础设置
class Config:
    # 设置密匙
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'GG0914ZH'
    # 每次请求结束后自动提交数据库变动设置为true
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    # Flask-SQLAlchemy 将会追踪对象的修改并且发送信号
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # 邮箱主题前缀
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky-test]'
    # 寄件人
    FLASKY_MAIL_SENDER = '某管理员 <gggzh@139.com>'
    # 文章分页显示数
    FLASKY_POSTS_PER_PAGE = 10
    # 粉丝页分页显示数
    FLASK_FOLLOWERS_PER_PAGE = 15
    # 评论分页显示数
    FLASKY_COMMENTS_PER_PAGE = 15
    # 管理员邮箱
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    # 查询速度慢于多少秒
    FLASKY_SLOW_DB_QUERY_TIME = 0.5
    # SQLAlchemy记录查询
    SQLALCHEMY_RECORD_QUERIES = True
    # SSL协议开关
    SSL_DISABLE = True
    MAIL_SERVER = 'smtp.139.com'  # 服务器地址
    MAIL_PORT = 465  # 服务器端口号
    MAIL_USE_TLS = False  # 默认为False
    MAIL_USE_SSL = True  # 打开邮箱SSL安全协议
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  # 在环境变量中获取账号
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # 在环境变量中获取密码
    
    @staticmethod
    def init_app(app):
        pass


# 开发配置
class DevelopmentConfig(Config):
    DEBUG = True # 调试开关
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    
    
    
# 测试设置
class TestingConfig(Config):
    TESTING = True # 测试开关
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # 发送错误到管理员邮箱
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.FLASKY_MAIL_SENDER,
            toaddrs=[cls.FLASKY_ADMIN],
            subject=cls.FLASKY_MAIL_SUBJECT_PREFIX + ' Application Error',
            credentials=credentials,
            secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}