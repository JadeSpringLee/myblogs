from flask import Blueprint, render_template

blog_bp = Blueprint('blog', __name__)

@blog_bp.route('/')
def hello():
    return render_template('base.html')

@blog_bp.route('/about')
def about():
    return '关于页面'

@blog_bp.route('/category/<int:category_id>')
def category(category_id):
    return '分类页面 '