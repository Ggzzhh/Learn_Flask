学习狗书产生的代码以及笔记
=======================

Jinja2模版在html中的各种应用
--------------------------

* {{ 变量|过滤器 }}
    * 如  ```Hello, {{ name|capitalize }} ```把name变为首字母大写的方式展现出来

* 控制结构

    * 如 if-else 结构
        ```html
        {% if user %}
            Hello, {{ user }}!
        {% else %}
            Hello, Stranger!
        {% endif %}
        ```

    * 如 for 循环结构
        ```html
        <ul>
            {% for comment in comments %}
                <li>{{ comment }}</li>
            {% endfor %}
        </ul>
        ```

    * Jinja2 支持宏  宏是类似函数的存在 如：
        ```html
        {%　macro render_comment(comment)　%} # macro就是宏
            <li>{{ comment }}</li>
        {% endmacro %}

        {% for comment in comments %}
            {{ macro.render_comment(comment) }}
        {% endfor %}
        ```

    * 导入其他文件中存在的宏
        ```html
        {% import 'macros.html' as macros %}
        <ul>
            {% for comment in comments %}
                {{ macros.render_comment(comment) }}
            {% endfor %}
        </ul>
        # 导入整个文件
        {% include 'common.html' %}
        ```

    * 可以继承其他模版 比如头部信息或者导航等设置成一个基础模版 'base.html'
        * 例子参见templates/base.html 以及 index.html

    * flask拓展模块——flask-bootstrap
        * 基本用法参照例子templates/base.html
        * 如果要在已经有内容的块中添加新内容需要使用super()，如：
            ```html
            {% block scripts %}
            {{ super() }}
            <script type="text/javascript" src="my-script.js"></script>
            {% endblock %}
            ```

    * 自定义错误页面
        * py文件中写入以下内容（例）
            ```python
            @app.errorhandler(404)
            def page_not_found(e):
                return render_template('404.html'), 404

            @app.errorhandler(500)
            def internal_server_error(e):
                return render_template('500.html'), 500
            ```

        * 其余内容404.html在templates中

    * 连接 返回地址时 可使用函数url_for() 会返回相对地址 _external关键字参数默认为false
        ```html
        url_for('user', name='john', _external=True)
        #http://localhost:5000/user/john
        url_for('index', page=2) # /?page=2
        ```

    * 静态文件 比如css文件或者图片 例子是标签地址
        ```html
        {% block head %}
        {{ super() }}
        <link rel="shortcut icon" href="{{ url_for('static',
            filename = 'favicon.ico') }}" type='image/x-icon' />
        {% endblock %}
        ```

    * 时间渲染可使用flask拓展flask-moment模块 书中例子未实现


Web表单
-------
* 安装flask拓展--flask-wtf 处理表单

* 跨站请求伪造保护
        用app.config字典可以用来存储框架、拓展和程序本身的配置变量，这个对象还提供
    一些方法也可以从文件或者环境中导入配置量.

* 表单类
    示例代码参见hello.py
    * post提交后刷新页面浏览器会重新发送之前已经发送过的最后一个请求，所以最好的处理
    方式是让最后一个请求是get，也就是Post/重定向/Get模式.
    * 这个方式需要把post的请求内容存储起来 避免丢失 用session['内容']来存储在cookie中！

数据库
------
* 下载使用flask-SQLAlchemy管理数据库
    * 数据可参考python中文学习大本营 http://www.pythondoc.com/
    * 简单例子可在hello.py中查看
    * 例子中的一对多 中的一要设置关系属性 relationship(关联表名, backref, lazy等) 具体如下：
        * backref 对关联的表的反向引用 比如role中设置的backref=role 关联的表示users
        那么users的实例就可以调用user1.role来查看user1的角色了
        * lazy 指定如何加载相关记录
        * 'select' (默认值) 就是说 SQLAlchemy 会使用一个标准的 select 语句必要时一次加载数据。
        * 'joined' 告诉 SQLAlchemy 使用 JOIN 语句作为父级在同一查询中来加载关系。
        * 'subquery' 类似 'joined' ，但是 SQLAlchemy 会使用子查询。
        * 'dynamic' 在有多条数据的时候是特别有用的。不是直接加载这些数据，也就是多对多。
            它返回一个尚未执行的查询，可以在其之上添加过滤器。
        * 定义backref的lazy属性： backref = db.backref('role', lazy='dynamic')
        * 如果要变成一对一关系： uselist = False 即可，表示不适用列表
        * order_by 指定关系中的排序方式
        * secondary 指定多对多中的关系表的名字
        * secondaryjoin 无法自行决定时，指定多对多关系中的二级联结条件

* 数据库操作

    * 创建表
        * db.create_all() 根据模型创建数据库
        * 因为它不会更新已有表 所以表结构更改后需要粗暴的先删除旧表再创建新表
        * db.drop_all() 删除所有表？？然后再创建 db.create_all()

    * 插入行
        * 首先为数据库表中插入内容，如： user_john = User(username='john', role=admin_role)
        此时所有的Id都为None 因为还未提交到数据库  所以Id未写入数据。
        * 然后添加到数据库的会话中，db.session.add(user_john)或db.session.add_all([user1,
        user2, user3 ...])
        * 最后写入进数据库 db.session.commit() 之后id属性就被赋值了
        * 数据库会话也可以回滚，调用 db.session.rollback()后，添加到数据库会话中的所有对象
        都会还原到它们在数据库时的状态，或者取消当前修改。

    * 修改行
        * 在数据库会话上用add()方法也能更新模型。
        ```python
        admin_role.name = 'Nwe Name'
        db.session.add(admin_role)
        db.session.commit()
        ```

    * 删除行
        * 使用delete()方法
        ```python
        db.session.delete(mod_role)
        db.session.commit()
        ```
        * 插入跟删除和更新一样，提交（commit)后才会执行

    * 查询行
        * 查询某个表的所有内容 Table.query.all()
        * 使用过滤器(filter)可以更精确的查询
            如：User.query.filter_by(role=user_role).all()
        * 常用过滤器如下：
        ```python
         filter()       # 把过滤器添加到一个原查询上，返回一个新查询
         filter_by()    # 把等值过滤器添加到一个原查询上，返回一个新查询
         limit()        # 使用指定的值限制原返回查询的结果数量，返回一个新查询
         offset()       # 偏移原查询返回的结果，返回一个新查询
         order_by()     # 根据指定条件对原查询进行排序，返回一个新查询
         group_by()     # 根据指定条件对原查询结果进行分组，返回一个新查询
        ```
        * 通过调用all()方法执行查询，以列表的形式返回所有查询结果
        * first() 或 first_or_404() 返回第一个查询结果，如果没有返回None或者终止请求，返回404错误。
        * get() 或 get_or_404() 返回指定主键对应的行，如果没有返回None或者终止请求，返回404错误。
        * count() 返回所有结果的数量
        * paginate() 返回一个分页对象？, 它包含指定范围内的结果

    * 在视图上操作数据库 见hello.py
    * 为shell命令添加一个上下文 使其自动导入数据库实例和模型 之后可免于每次在shell中导入数据库
        可使用 装饰器@manager.shell 修饰函数 例：
        ```python
        @manager.shell
        def make_shell_context():
            return dict(app=app, db=db, User=User, Role=Role)

        ```

    * 使用 Flask-Migrate 实现数据库迁移
        * 变更表结构后最好使用数据库迁移 这样能避免数据丢失或者重新写入
        * 安装后的配置请参见hello.py
        * 配置迁移 并将MigrateCommand类附加到manager对象上
            然后再命令行运行 init 子命令创建迁移仓库
            如： python3 hello.py db init
        * 创建迁移脚本
            upgrade()函数把迁移中的改动应用到数据库， downgrade()函数则是将改动删除
            使用migrate子命令自动创建迁移脚本 不一定总是对的 需要检查
            如： python3 hello.py db migrate -m "initial migrate"
        * 检查并且修整好迁移脚本后 使用db upgrade 命令把迁移应用到数据库中
            python3 hello.py db upgrade



电子邮件
-------

* 包装了python内置函数smtplib的flask拓展 Flask-Mail
    * 为了避免直接把数据写入到文件中 所以把账户跟密码写入环境变量
        * Linux或Mac：
            `$ export MAIL_USERNAME=<Email username>`
            `$ export MAIL_PASSWORD=<Email password>`
            查看 export
        * Windows：
            命令提示符：
            `$ set MAIL_USERNAME=<Email username>`
            `$ set MAIL_PASSWORD=<Email password>`
            查看 ：set
            PowerShell:
            `$env:MAIL_USERNAME='<EMAIL username>'`
             查看： ls env:
        * mac中输入export查看设置的账号密码
    * 进行初始化Flask-Mail 在hello.py中 因为需要打开设置 所以没有试验
    * 因为可能会卡顿所以需要异步发送邮件 使用threading


大型程序的结构
------------

* 基本项目结构 重构hello.py
    ```
    |-flasky
        |-app/  # Flask程序一般都保存在这里
            |-templates/
            |-static/
            |-main/
                |-__init__.py
                |-errors.py
                |-forms.py
                |-views.py
            |-__init__.py
            |-email.py
            |-models.py
        |-migrations/ # 迁移数据库脚本
        |-tests/ # 单元测试
            |-__init__.py
            |-test*.py
        |-venv/ # 存放虚拟环境
        |-requirements.txt # 列出所有依赖包，以便在其他电脑中重新生成相同的虚拟环境
        |-config.py # 存储配置
        |-manage.py # 用于启动程序以及其他程序任务
    ```

    * 定义了工厂函数后 让定义路由变得复杂 所以采用蓝本 Blueprint 在main的init中
    * 测试章节 在tests中


用户认证
-------
* 有新的依赖包
    * Flask-Login 管理登录的用户会话
    * Werkzeug 计算密码散列值并进行核对
    * itsdangerous 生成并核对加密安全令牌

* 使用Werkzeug实现密码散列
    * generate_password_hash(password, method=pbkdf2:sha1, salt_lenget=8)
        这个函数将原始密码作为输入， 以字符串形式输入密码散列值，输入加密后的值可保存
        在数据库中.
    * check_password_hash(hash, password): 这个函数的参数是从数据库中获取的密码散列值
    和用户输入的密码，返回值true 则表明密码正确

* 不同的程序功能使用不同的蓝本 创建认证蓝本auth
    创建蓝本的流程
    1. 在文件夹的__init__.py中创建蓝本 先引入蓝本 然后创建 最后导入视图函数
    2. 设置视图函数
    3. 在app/__init__中附加蓝本

* 使用Flask-login认证
    * 要使用flask-login需要实现四个方法
    * 这些可以在模型中实现 也可以采用默认实现 在Flask-login中有一个UserMixin类其中包含这些
        方法（is_authenticated(是否登录), is_active(是否允许登录)
        is_anonymous(是否普通用户)  get_id(返回用户唯一Id)）

* 使用itsdangerous生成确认令牌
    * 导入TimedJSONWebSignatureSerializer类
    ```python
    from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
    ```
    * Serializer接收一个密匙，生成一个有过期时间的JSON WEB签名
    * dumps()方法为指定的数据生成一个加密签名
    * loads()方法可以解码dumps()生成的的加密令牌，如果正确返回原数据，否则抛出异常
    ```python
    s = Serializer(密匙, expires_in=3600) # 过期时间是3600s
    token = s.dumps(数据)
    data = s.loads(token) # data 值 数据
    ```

* 出现的错误或者重要的事情
    * 发送邮件会出现多种小错误 比如环境变量中的账号密码错误
    * 自己实现修改密码以及重设密码、修改邮箱的功能
    * _external=True 参数要求程序生成完整的 URL，其中包含协议(http:// 或 https://)、主机名和端口。
    * url_for 作用的是函数，而不是路径
    * 当我们在表单类里面定义了诸如 “Validate_字段名”形式的函数时，
      Flask在检查相应字段时会对该函数一起进行调用，
      利用这种形式我们可以自定义一些限制规则，如下面的代码，
      我们定义了一个函数validate_new_email用来检查email是否在数据库中存在。
      ```python
      def validate_new_email(self, field):
          """当函数以validate_打头时， 检查字段时候会一起调用本函数"""
          if User.query.filter_by(email=field.data).first():
              raise ValidationError("该邮箱已经被注册！")
      ```

* 用户角色
    * 创建角色表，（id，名字，默认值，权限，用户）
        只有一个角色的默认值设置为true 其余为默认的False

    * flasky来说，程序的权限分为：
        关注用户        0b0000000001  (0x01)    关注其他用户
        发表评论        0b0000000010  (0x02)    在他人写的文章中发布评论
        撰写文章        0b0000000100  (0x04)    写自己的原创文章
        管理评论        0b0000001000  (0x08)    查处他人发布的不当评论
        管理权限        0b1000000000  (0x80)    管理网站，管理员

    * 权限常量
        ```python
        class Permission:
            FOLLOW = 0x01
            COMMENT = 0x02
            WRITE_ARTICLES = 0x04
            MODERATE_COMMENTS = 0x08
            ADMINISTER = 0x80
        ```
        还有三个权限未定义 待拓展

    * 用户角色
        匿  名    0b0000000000 (0x00)     未登录的用户。只有阅读权限
        用  户    0b0000000111 (0x07)     可以发布文章，发表评论和关注其他的权限，默认角色
        协  管    0b0000001111 (0x0f)     增加审查不当评论的权限
        管  理    0b1111111111 (0xff)     具有所有权限，包括修改其他用户角色的权限

    * 这些权限以及角色都是通过大小来判断的 在python中插入时使用
        "User": (0x01 | 0x02 | 0x04) 来确定权限
        这是按位或运算  结果为0x07跟用户的数字是一样的
        比如 0x01 | 0x02  ==  00000001 | 00000010 = 00000011 # 十六进制中的0x03
        0x03 | 0x04 == 00000011 | 00000100 = 00000111 # 十六进制0x07
        按位或运算 就是把其余进制的数字转换为2进制然后按着位数进行或运算
        按照 1|1 = 1  1|0 = 1 0|0 = 0 进行运算然后得出结果即可

        & 是按位与 与按位或相同 不同的是进行与运算
        按照 1&1 = 1 1&0 = 0 0&0 = 0 来进行运算 然后转换为所需进制即可

    * 赋予角色
        通过修改User类来赋予角色

    * 角色验证
        * 先通过角色的所有权限进行（按位或）运算得出结果后
        和要进行比较的权限进行 （按位与）运算 然后比较结果
        如果角色中包含请求的所有权限位 则返回True
        ```python
        def can(self, permissions):
            """检查用户是否有指定权限"""
            return self.role is not None and (self.role.permissions &
                                              permissions) == permissions
        ```

        * 出于一致性考虑加入了游客类，这样程序不用先检查用户是否登录，
            就能调用current_user.can() 以及 current_user.is_administrator()

        * 使用自定义修饰器，让视图函数只对有特定权限的用户开放，详情参见app/decorators.py

        * @admin_required 可以还原成 @permission_required(Permission.ADMINISTER)
        作用跟@login_required几乎一样

        * 上下文管理器 也可以叫做引用池
            下面的代码是把Permission类加入模版上下文
            之后即可在HTML页面中进行调用
        ```python
        @main.app_context_processor
        def inject_permission():
            return dict(Permission=Permission)
        ```
