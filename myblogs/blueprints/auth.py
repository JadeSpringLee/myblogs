from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    return '登陆界面'

@auth_bp.route('/logout')
def logout():
    return '登出'