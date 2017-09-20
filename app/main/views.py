#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""这个是视图路由，类似网站地图"""

from datetime import datetime
from flask import render_template, session, redirect, url_for, \
    abort, flash, request, current_app, make_response
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, \
    PostForm, CommentForm
from .. import db
from ..models import User, Role, Permission, Post, Comment
from ..decorators import admin_required, permission_required


@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'


@main.route('/', methods=['GET', 'POST'])
def index():
    # 获取首部user-agent（浏览器信息）
    # user_agent = request.headers.get('User-Agent')
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    # 按照书写时间降序排列
    # posts = Post.query.order_by(Post.timestamp.desc()).all()
    # 开始分页
    # 获取渲染页数 默认值是1 也就是从首页开始 类型是整数
    page = request.args.get('page', 1, type=int)

    show_followed = False
    if current_user.is_authenticated:
        # 获取cookie值 如果没有 就设定值为空
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    # paginate(page, ...)的返回值是pagination类型的 page是必须参数, per_page是每页显示数
    # error_out 如果为True 超出页数范围会返回404 否则为空列表
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False
    )
    posts = pagination.items
    return render_template("index.html", form=form, posts=posts,
                           show_followed=show_followed, pagination=pagination)


@main.route('/user/<username>')
def user(username):
    """该网页是用户资料页面"""
    web_user = User.query.filter_by(username=username).first_or_404()
    if web_user is None:
        abort(404)
    posts = web_user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=web_user, posts=posts)


@main.route('/edit-profile', methods=["POST", "GET"])
@login_required
def edit_profile():
    """用户资料编辑页面"""
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash("你的资料已经更改！")
        return redirect(url_for('main.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    print('这里')
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=["GET", "POST"])
@login_required
@admin_required
def edit_profile_admin(id):
    """管理员编辑页面"""
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash("这个人资料已经更改！")
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/post/<int:id>', methods=["POST", "GET"])
def post(id):
    """文章固定连接"""
    my_post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=my_post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash('你发布了一条评论！')
        # page=-1 用来请求评论的最后一页，也就是发完评论之后直接可以看见自己的评论
        return redirect(url_for('.post', id=my_post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (my_post.comments.count() - 1) // \
            current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = my_post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False
    )
    comments = pagination.items
    return render_template('post.html', posts=[my_post], form=form,
                           comments=comments, pagination=pagination)


@main.route('/edit/<int:id>', methods=["GET", "POST"])
@login_required
def edit(id):
    """编辑文章路由视图"""
    post = Post.query.get(id)
    if post is None:
        return redirect(url_for('.index'))
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.submit.data and form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('内容已经更新！')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form, posts=post)


@main.route('/edit/<int:id>/delete', methods=["POST"])
@login_required
def delete(id):
    """删除文章用"""
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    try:
        db.session.delete(post)
    except:
        flash('删除失败！ 原因？？？')
        return redirect(url_for('.index'))
    flash('删除成功!')
    return redirect(url_for('.index'))


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    """关注用户"""
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('查无此人！')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash("你已经关注过他了！")
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash("你关注了%s!" % username)
    return redirect(url_for('.user', username=username))


@main.route('/un_follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def un_follow(username):
    """取消关注"""
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('查无此人！')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash("你关注了%s!" % username)
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash("你已经不再关注%s了!" % username)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    """用户的粉丝列表页"""
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('查无此人！')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASK_FOLLOWERS_PER_PAGE'],
        error_out=False
    )
    follows = [{'user': item.follower, 'timestamp': item.timestamp} for item in
               pagination.items]

    return render_template('follow.html', user=user, title='的粉丝',
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed_by/<username>')
def followed_by(username):
    """用户关注的人"""
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('查无此人！')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASK_FOLLOWERS_PER_PAGE'],
        error_out=False
    )
    follows = [{'user': item.followed, 'timestamp': item.timestamp} for item in
               pagination.items]

    return render_template('follow.html', user=user, title='关注的人',
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


@main.route('/all')
@login_required
def show_all():
    """返回一个响应，这个响应设置了cookie['show_followed']的值为空(默认也是空)"""
    # 生成一个响应 因为cookie只能在响应中设置
    resp = make_response(redirect(url_for('.index')))
    # 给响应设置一个最长保存时间一个月的cookie
    resp.set_cookie('show_followed', "", max_age=30*24*60*60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    """
    返回一个响应，这个响应设置了cookie['show_followed']的值为1
    点击这个地址会显示已关注的人并且返回至首页
    """
    # 生成一个响应 因为cookie只能在响应中设置
    resp = make_response(redirect(url_for('.index')))
    # 给响应设置一个最长保存时间一个月的cookie
    resp.set_cookie('show_followed', "1", max_age=30*24*60*60)
    return resp


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    """管理评论"""
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False
    )
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    """启用该评论"""
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    """禁用评论"""
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))
