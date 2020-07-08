import os
import sys

#  定位到项目根目录
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# SQLite URI 兼容
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

#  基本配置
class BaseConfig(object):
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev key')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SEVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('Myblogs Admin', MAIL_USERNAME)

    MYBLOGS_EMAIL = os.getenv('MYBLOGS_EMAIL')
    MYBLOGS_POST_PER_PAGE = 10
    MYBLOGS_MANAGE_POST_PER_PAGE = 15
    MYBLOGS_COMMENT_PER_PAGE = 15


#  开发环境配置
class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir, 'data-dev.db')


#  测试环境配置
class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_UTI = f'{prefix}:memory:'


# 生产环境配置
class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', prefix + os.path.join(basedir, 'data.db'))

config = {
    'development' : DevelopmentConfig,
    'testing' : TestingConfig,
    'production' : ProductionConfig
}

