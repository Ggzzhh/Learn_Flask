# -*- coding: utf-8 -*-
import unittest
from flask import current_app
from app import create_app, db

class BasicTestCase(unittest.TestCase):
    # 在测试启动前运行 创建一个app 然后把其中的上下文推送出去并创建数据库
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    # 在测试启动后运行 移除会话 删除数据表 以及弹出上下文？
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # 断言app不存在
    def test_app_exists(self):
        self.assertFalse(current_app is None)

    # 断言测试正在运行
    def test_app_testing(self):
        self.assertTrue(current_app.config['TESTING'])