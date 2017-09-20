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

    * iframe中提交表单 方法一： form属性添加target='_parent'
    注意：target='_parent '如果后面多加了空格 提交后会新打开一个网页


博客文章等
----------

* sqlAlchemy 数据库 关联外键时使用表名+字段  如:
    ```python
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    ```
* 设定关系时使用类名 如：
    ```python
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    ```
* 部分表单中这样可以添加属性 :
    ```python
    body = TextAreaField("你在想什么？", validators=[DataRequired()],
                         render_kw={"rows": 3})
    ```
    * 使用render_kw={}添加自己想要的属性
* 文章分页需要包含大量数据的测试数据库，自动化添加可以使用ForgeryPy 来生成虚拟信息
* 区分生产环境跟开发环境
* Table.query.offset(num).first() 查询过滤器 会跳过参数中指定的记录数量。
* Flask-SQLAlchemy 分页对象属性
    * items     当前页面中的记录
    * query     分页的查询源
    * page      当前页数
    * perv_num  上一页的页数
    * next_num  下一页的页数
    * has_next  如果有下一页就返回True
    * has_perv  如果有上一页就返回True
    * pages     查询得到的总页数
    * per_page  每页显示的查询数量
    * total     查询返回的总记录数
* Flask-SQLAlchemy 分页对象方法
    * iter_pages(       一个迭代器，返回分页导航中显示的页数
    * left_edge=2,      这个列表最左边显示2页
    * left_current=2,   当前页面的左边显示2页
    * right_current=3,  当前页面的右边显示3页
    * right_edge=2)     这个列表最右边显示2页
    * 如： 100页的列表、当前为50页  会显示：
        1、2、...、48、49、50、51、52、53、...、99、100
    * prev()            上一页的分页对象
    * next()            下一页的分页对象
* 新建一个专门存放宏的文件 _macros.html 存放分页模版宏

* 使用Markdown 和 Flask-PageDown支持富文本文章, 所需环境为
    * PageDown: 使用JavaScript实现的客户端Markdown到HTML的转换程序
    * flask-PageDown: 为Flask包装的PageDown, 集成到Flask-WTF表单中
    * markdown: 使用python实现的服务器端 Markdown到HTML的转换程序
    * bleach: 使用python实现的 HTML清理器
    * pip 安装均为小写即可

* 为了安全起见， post只发送markdown源文本，然后在服务器上使用markdown转换为
    html文件，然后使用bleach进行清理，确保只有几个允许使用的html标签

* 每个文章需要一个单独的页面，这样方便分享或者编辑


添加关注
-------

* 数据库，多对多关系
    * 需要定义一个中间表来实现多对多
    * 中间表定义两个一对多的关系
    * lazy='dynamic' 后返回的查询可以接受额外的过滤器

* 自引用关系
    比如关注 就是一个用户关注另一个用户 引用的是同一个表
    这就是简单的自引用关系  关注者(follower) 跟 被关注者(followed)
    * 为了消除外键间的歧义，定义关系时必须使用可选参数`foreign_keys`指定外键

* cascade 参数，按照书中的例子，我理解是：
    * 在操作父对象（User表）的时候，对相关对象（Follow表）的影响
    * cascade='all, delete-orphan' 个人理解为：A关注了B,C,D! B用户被删除了，
    这个属性可以把A的关注列表中的B 也删除，变为C,D。

* 添加关注的github提交为2017-09-15-a
* 使用数据库联结查询所关注用户的文章
    * 需要用到join 联结关键字 把两个表联结拼合在一起
    * 例子： 需要先查询所关注的用户都有谁（表1），之后查询这些用户的文章(表2)
    * Flask-SQLAlchemy查询用例子：
        `db.session.query(Post).select_from(Follow).\
        filter_by(follower_id=self.id).\
        join(Post, Follow.followed_id == Post.author_id)`

    * 来分解一下, 因为牵扯的表比较多 所以用基础查询 self.id 是用户自身的id
        * db.session.query(Post)            指明这个查询要返回Post对象
        * select_from(Follow)               意思是这个查询从Follow模型开始
        * filter_by(follower_id=self.id)    使用关注用户过滤follows表
        * join(...)                         联结filter_by()得到的结果和Post对象

    * 调换过滤器和联结的顺序可以简化这个查询：
    `Post.query.join(Follow, Follow.followed_id == Post.author_id)\
        .filter(Follow.follower_id == self.id)`
    * 这两种结构查询生成的原生态SQL语句是一样的， 不同的是一个先联结再过滤，
    第二个先过滤再联结
    * 实现提交为2017-09-15-b

* 在已关注的人的文章中查看自己 解决办法一： 把自己添加进已关注的人中
    然后在渲染时数量-1 ，调整粉丝和关注用户的列表，不再显示自己。
    最后单元测试会收到自关注的影响，注意调整。


REST风格的应用程序接口--API
-------------------------

* RIA(富互联网应用)架构中，服务器的主要功能是为客户提供`数据存取`服务。
    在这种模式下，服务器变成了`Web服务`或`应用程序接口(API)`

* REST 翻译为 表现层状态转移

* 关于 REST怎么简单解释...
> 以下引用自：[知乎上的某REST话题](https://www.zhihu.com/question/28557115)

* 简单理解为：`URL定位资源，HTTP动词描述操作。`

* 再直白点就是：
    * `看URL就知道要什么`
    * `看HTTP Method 就知道干什么`
    * `看HTTP status code 就知道结果是什么`

* REST架构的特征（优点）
    * 客户端-服务器分离：
        * 操作简单，高性能，低成本，允许组件分别优化。
    * 无状态（Stateless）：从客户端的每个请求要包含服务器所需要的所有信息
        * 提高可见性（可以单独考虑每个请求）
        * 提高了可靠性（更容易从局部故障中修复）
        * 提高可扩展性（降低了服务器资源使用）
    * 缓存（Cachable）：服务器返回信息必须被标记是否可以缓存，
                       如果缓存，客户端可能会重用之前的信息发送请求。
        * 减少交互次数
        * 减少交互的平均延迟
    * 分层系统：系统组件不需要知道与他交流组件之外的事情。封装服务，引入中间层。
        * 限制了系统的复杂性
        * 提高可扩展性
    * 统一接口（Uniform Interface）： 一般为HTTP
        * 提高交互的可见性
        * 鼓励单独改善组件
    * 支持按需代码（Code-On-Demand 可选）： 客户端可以选择从服务器上下载代码，在客户端的环境中执行。
        * 提高可扩展性

* REST中资源就是一切，资源为REST架构方式的核心概念。
    * 一般来说：URL的风格为名词，并且推荐使用复数
    * 如：GET /api/posts    DELETE /api/comments
    * 因此 GET /posts/<int: id>/delete 这样的URL  ####绝对不是RESTful架构风格

* ###REST架构API中使用的HTTP请求方法
    * GET(获取资源) POST(新建或更新资源) PUT(更新资源) DELETE(删除资源)
    * 响应状态码一般为200

* Flask比较适用于用json(JavaScript对象表示法)传递资源，如：
    ```python
        {
        "url": "http://www.example.com/api/posts/12345",
        "title": "Writing RESTful APIs in Python",
        "author": "http://www.example.com/api/users/2",
        "body": "... text of the article here ...",
        "comments": "http://www.example.com/api/posts/12345/comments"
        }
    ```
* 使用FLASK创建RESTful： 参见app/api_1_0

* 错误处理
    * REST会在响应中发送HTTP状态码，并将额外信息放入响应主体。
    * 一般来说：
    HTTP状态码     名　　称                               说　　明
        200     OK（成功）                               请求成功完成
        201     Created（已创建）                        请求成功完成并创建了一个新资源
        400     Bad request（坏请求）                    请求不可用或不一致
        401     Unauthorized（未授权）                   请求未包含认证信息
        403     Forbidden（禁止）                        请求中发送的认证密令无权访问目标
        404     Notfound（未找到）                       URL 对应的资源不存在
        405     Method not allowed（不允许使用的方法）    指定资源不支持请求使用的方法
        500     Internal server error（内部服务器错误）   处理请求的过程中发生意外错误

* 使用Flask-HTTPAuth认证用户
    * 　示例： app/api_1_0/authentication.py
    * 关于全局对象g 它是一个请求上下文？ 只存活于当前请求中 换一个请求就换了一个g

* 关于jsonify() 函数是把python中的dict类型转换成json类型
    * jsonify() 返回的数据中，中文显示Unicode，
    * 改正方法 app.config['JSON_AS_ASCII'] = False ??
    * json.dumps()解决同样的问题可以加入ensure_ascii=False


