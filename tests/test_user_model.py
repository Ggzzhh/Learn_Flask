# -*- coding: utf-8 -*-
import  unittest
from app.models import User

class UserModelTestCase(unittest.TestCase):
    """对用户注册的密码进行测试"""
    def test_password_seter(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)