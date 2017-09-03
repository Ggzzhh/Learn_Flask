# -*- coding: utf-8 -*-
import os
# 导入Flask， 返回内容， 提供的模版
from flask import Flask, request, render_template
# 设置一个响应对象, 用户对话， 地址, flash
from flask import make_response, session, url_for, flash
# 重定向, abort终止（用于处理错误）
from flask import redirect, abort
# flask拓展 flask-script
from flask_script import Manager
# flask拓展 flask-bootstrap
from flask_bootstrap import Bootstrap
# flask拓展 flask-wtf
from flask_wtf import FlaskForm
# stringField 就是type=text的input  submit同理
from wtforms import StringField, SubmitField
# 导入验证器 的要求
from wtforms.validators import DataRequired
# 导入数据库
from flask_sqlalchemy import SQLAlchemy
# 配置flask_migrate
from flask_migrate import Migrate, MigrateCommand
# smtp邮箱
from flask_mail import Mail



basedir = os.path.abspath(os.path.dirname(__file__)) # 获取文件地址

app = Flask(__name__) # 创建一个app


# App 相关设置
# 设置密匙
app.config['SECRET_KEY'] = '!(()(!$'
# 设置SQLite数据库地址
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
# 每次请求结束后自动提交数据库变动设置为true
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
# Flask-SQLAlchemy 将会追踪对象的修改并且发送信号
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# 邮箱相关设置
app.config['MAIL_SERVER'] = 'smtp.qq.com' # 服务器地址
app.config['MAIL_PORT'] = 465 # 服务器端口号
app.config['MAIL_USE_TLS'] = True # 开启安全协议
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') # 在环境中获取账号密码
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')


db = SQLAlchemy(app) # 创建sqlalchemy实例数据库
manager = Manager(app) # 对app采用管理
bootstrap = Bootstrap(app) # 使用bootstrao对app进行修饰
migrate = Migrate(app, db) # 配置迁移 并将MigrateCommand类附加到manager对象上
manager.add_command('db', MigrateCommand)
mail = Mail(app) # 对app使用smtp邮箱脚本

# 创建一个表单类
class NameForm(FlaskForm):
    name = StringField('你的名字是？', validators=[DataRequired()])
    submit = SubmitField('submit')
    


# 创建数据库表
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name
    
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    
    def __repr__(self):
        return '<User %r>' % self.username


# 为shell命令添加一个上下文 使其自动导入数据库实例和模型
@manager.shell
def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)

# manager.add_command("shell", Shell(make_context=make_shell_context))
# 返回的页面配置

@app.route('/', methods=['GET', 'POST'])
def index():
    # 获取首部user-agent（浏览器信息）
    # user_agent = request.headers.get('User-Agent')
    form = NameForm()
    # 如果提交了表单
    if form.validate_on_submit():
        # 查询数据库中是否有该用户
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = '请输入姓名？？？'
        return redirect(url_for('index'))
    return render_template('index.html', form = form, name = session.get(
        'name'), known = session.get('known', False))
        

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

@app.route('/response')
def res():
    response = make_response('<h1>这个对象运输一个cookie！</h1>')
    response.set_cookie('answer', '42')
    return response

@app.route('/redirect/<id>')
def redirect_to_baidu(id):
    user = id
    if not user:
        abort(404)
    # return redirect('https://www.baidu.com')
    return id

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('404.html'), 500

if __name__ == "__main__":
    manager.run()