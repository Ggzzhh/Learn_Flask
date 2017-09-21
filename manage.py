#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
from app import create_app, db
from app.models import User, Role, Post
from flask_script import Manager, Server
from flask_migrate import Migrate, MigrateCommand

# 只有在测试的情况下才使用coverage查询覆盖率
COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    # 函数 coverage.coverage() 用于启动覆盖检测引擎。
    # branch=True 选项开启分支覆盖分析
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


@manager.shell
def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Post=Post)
manager.add_command('db', MigrateCommand)


# 这个装饰器让函数名就是命令名
@manager.command
def test(coverage=False):
    """进行单元测试"""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('内容覆盖率')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML 版本: file://%s/index.html' % covdir)
        COV.erase()


@manager.command
def profile(length=25, profile_dir=None):
    """启动应用程序之后进行代码查询"""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(
        app.wsgi_app, restrictions=[length], profile_dir=profile_dir
    )
    app.run()

if __name__ == "__main__":
    manager.run()