#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
basedir = os.path.abspath(os.path.dirname(__file__))

# 基础设置
class Config:
    # 设置密匙
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gzhnyc'
    # 每次请求结束后自动提交数据库变动设置为true
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    # Flask-SQLAlchemy 将会追踪对象的修改并且发送信号
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # 邮箱主题前缀
    FLASK_MAIL_SUBJECT_PREFIX = '[Flasky-test]'
    # 寄件人
    FLASK_MAIL_SENDER = '某管理员 <3272377652@qq.com>'
    # 管理员邮箱
    FLASK_ADMIN = os.environ.get('FLASK_ADMIN')
    
    @staticmethod
    def init_app(app):
        pass


# 开发配置
class DevelopmentConfig(Config):
    DEBUG = True # 调试开关
    MAIL_SERVER = 'smtp.qq.com' # 服务器地址
    MAIL_PPORT = 465 # 服务器端口号
    MAIL_USE_TLS = True # 打开安全协议
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') # 在环境变量中获取账号
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') # 在环境变量中获取密码
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    
    
    
# 测试设置
class TestingConfig(Config):
    TESTING = True # 测试开关
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    
# 生产配置
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    
config = {
    'development' : DevelopmentConfig,
    'testing' : TestingConfig,
    'production' : ProductionConfig,
    'default' : DevelopmentConfig
}