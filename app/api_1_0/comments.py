# -*- coding: utf-8 -*-
from flask import jsonify, g, url_for, current_app, request
from .. import db
from ..models import Post, Permission, Comment
from . import api
from .decorators import permission_required


@api.route('/comments/')
def get_comments():
    """获得评论以及分页"""
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False
    )
    comments = pagination.items
    _prev = None
    if pagination.has_prev:
        _prev = url_for('api.get_comments', page=page-1, _external=True)
    _next = None
    if pagination.has_next:
        _next = url_for('api.get_comments', page=page+1, _external=True)
    return jsonify({
        'comments': [comment.to_json() for comment in comments],
        'prev': _prev,
        'next': _next,
        'count': pagination.total
    })


@api.route('/comments/<int:id>/')
def get_comment(id):
    """获取单个评论"""
    comment = Comment.query.get_or_404(id)
    return jsonify(comment.to_json())


@api.route('/posts/<int:id>/comments/')
def get_post_comments(id):
    """获取某个微博的所有评论"""
    post = Post.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False
    )
    comments = pagination.items
    _prev = None
    if pagination.has_prev:
        _prev = url_for('api.get_post_comments', id=id, page=page-1,
                       _external=True)
    _next = None
    if pagination.has_next:
        _next = url_for('api.get_post_comments', id=id, page=page+1,
                       _external=True)
    return jsonify({
        'comments': [comment.to_json() for comment in comments],
        'prev': _prev,
        'next': _next,
        'count': pagination.total
    })


@api.route('/posts/<int:id>/comments/', methods=["post"])
@permission_required(Permission.COMMENT)
def new_post_comment(id):
    """给微博添加一个新评论"""
    post = Post.query.get_or_404(id)
    comment = Comment.from_json(request.json)
    comment.author = g.current_user
    comment.post = post
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_json()), 201, \
        {'Location': url_for('api.get_comment', id=comment.id, _external=True)}
