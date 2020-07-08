import os

import click
from flask import Flask, render_template

from myblogs.blueprints.admin import admin_bp
from myblogs.blueprints.auth import auth_bp
from myblogs.blueprints.blog import blog_bp
from myblogs.extensions import bootstrap, db, ckeditor, mail, moment
from myblogs.settings import config


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
    ckeditor.init_app(app)
    mail.init_app(app)
    moment.init_app(app)


def register_blueprints(app):
    app.register_blueprint(blog_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db)


def register_template_context(app):
    pass


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


def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        """Initialize the database."""
        if drop:
            click.confirm('This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')

