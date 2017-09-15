# -*- coding: utf-8 -*-
import unittest
from app.models import User, Role, Permission, AnonymousUser


class UserModelTestCase(unittest.TestCase):
    """对用户功能进行测试"""
    def test_password_setter(self):
        """测试能否设置密码"""
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        """测试能否直接调用密码属性"""
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        """测试两个用户的相同密码的hash值不同"""
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_roles_and_permissions(self):
        """测试普通用户可以写文章但是不能操作评论"""
        Role.insert_roles()
        u = User(email='text@example.com', password='word')
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        self.assertFalse(u.can(Permission.MODERATE_COMMENTS))

    def test_anonymous_user(self):
        """测试游客不许点关注"""
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))
