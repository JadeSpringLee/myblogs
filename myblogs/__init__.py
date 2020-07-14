import logging
import os
from logging.handlers import SMTPHandler, RotatingFileHandler

import click
from flask import Flask, render_template, request
from flask_login import current_user
from flask_sqlalchemy import get_debug_queries
from flask_wtf.csrf import CSRFError

from myblogs.blueprints.admin import admin_bp
from myblogs.blueprints.auth import auth_bp
from myblogs.blueprints.blog import blog_bp
from myblogs.extensions import bootstrap, db, ckeditor, login_manager, csrf, mail, moment, migrate
from myblogs.settings import config
from myblogs.models import Admin, Post, Category, Comment

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


#  工厂函数，接收配置名作为参数，返回创建好的程序实例。
def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('myblogs')
    app.config.from_object(config[config_name]) 
    
    register_logging(app)  # 注册日志处理器
    register_extensions(app)  # 注册扩展（扩展初始化）
    register_blueprints(app)  # 注册蓝本
    register_commands(app)  # 注册自定义 shell 命令
    register_errors(app)  # 注册错误处理函数
    register_shell_context(app)  # 注 shell 上下文处理函数命令
    register_template_context(app)  # 注册模板上下文处理函数
    return app
''' 
当这个工厂函数被调用后，首先创建一个特定配置类的程序实例，然后执行一系列注册函数
为程序实例注册日志处理器、扩展、蓝本、自定义shell命令、错误处理器、上下文处理器... 
在这个程序工厂的加工流水线的尽头，可以得到一个包含所有基本组件的可以直接运行的程序实例。
'''

def register_logging(app):
    pass


def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    ckeditor.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    migrate.init_app(app, db)


def register_blueprints(app):
    app.register_blueprint(blog_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db)


# 处理模板上下文
def register_template_context(app):
    @app.context_processor
    def make_template_context():
        admin = Admin.query.first()
        categories = Category.query.order_by(Category.name).all()
        if current_user.is_authenticated:
            unread_comments = Comment.query.filter_by(reviewed=False).count()
        else:
            unread_comments = None
        return dict(admin=admin, categories=categories)


def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500
        
    @app.errorhandler(CSRFError)
    def handlers_csrf_error(e):
        return render_template('errors/400.html', description=e.description), 400

# 注册自定义 shell 命令
def register_commands(app):
    # 初始化数据库
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='删除后重建.')
    def initdb(drop):
        """初始化数据库."""
        if drop:
            click.confirm('此操作将删除数据库，是否要继续？', abort=True)
            db.drop_all()
            click.echo('删除表.')
        db.create_all()
        click.echo('初始化数据库.')

    # 创建管理员账户
    @app.cli.command()
    @click.option('--username', prompt=True, help='The username used to login.')
    @click.option('--password', prompt=True, hide_input=True,
                  confirmation_prompt=True, help='The password used to login.')
    def init(username, password):
        """为您量身打造Blogs."""

        click.echo('初始化数据库...')
        db.create_all()

        admin = Admin.query.first()
        if admin is not None:
            click.echo('管理员已经存在，正在更新...')
            admin.username = username
            admin.set_password(password)
        else:
            click.echo('正在创建临时管理员帐户...')
            admin = Admin(
                username=username,
                blog_title='Blogs',
                blog_sub_title="",
                name='管理员',
                about=''
            )
            admin.set_password(password)
            db.session.add(admin)

        category = Category.query.first()
        if category is None:
            click.echo('正在创建默认文章类别...')
            category = Category(name='默认')
            db.session.add(category)

        db.session.commit()
        click.echo('管理员账户创建完成.')


    # 生成博客虚拟数据
    @app.cli.command()
    @click.option('--category', default=10, help='Quantity of categories, default is 10.')
    @click.option('--post', default=50, help='Quantity of posts, default is 50.')
    @click.option('--comment', default=500, help='Quantity of comments, default is 500.')
    def forge(category, post, comment):
        """生成虚拟数据."""
        from myblogs.fakes import fake_admin, fake_categories, fake_posts, fake_comments

        db.drop_all()
        db.create_all()

        click.echo('正在生成管理员数据...')
        fake_admin()

        click.echo('正在生成 %d 分类...' % category)
        fake_categories(category)

        click.echo('正在生成 %d 文章...' % post)
        fake_posts(post)

        click.echo('正在生成 %d 评论...' % comment)
        fake_comments(comment)

        click.echo('虚拟数据创建完成.')

