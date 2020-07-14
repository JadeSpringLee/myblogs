from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, SubmitField, SelectField, TextAreaField, ValidationError, HiddenField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional, URL

from myblogs.models import Category


# 登陆表单
class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 20)])
    password = PasswordField('密码', validators=[DataRequired(), Length(6, 128)])
    remember = BooleanField('记住我')
    submit = SubmitField('登陆')


class SettingForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    blog_title = StringField('博客标题', validators=[DataRequired(), Length(1, 60)])
    blog_sub_title = StringField('博客副标题', validators=[DataRequired(), Length(1, 100)])
    about = CKEditorField('关于页面', validators=[DataRequired()])
    submit = SubmitField('保存')


# 文章表单
class PostForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(), Length(1, 60)])
    author = StringField('作者', validators=[DataRequired(), Length(1,30)])
    category = SelectField('分类', coerce=int, default=1)
    body = CKEditorField('文章', validators=[DataRequired()])
    submit = SubmitField('发布')
    
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.category.choices = [(category.id, category.name)
                                 for category in Category.query.order_by(Category.name).all()] 


# 分类创建表单
class CategoryForm(FlaskForm):
    name = StringField('分类名称', validators=[DataRequired(), Length(1, 30)])
    submit = SubmitField('保存')

    def validate_name(self, field):
        if Category.query.filter_by(name=field.data).first():
            raise ValidationError('名称已存在！')


# 评论表单
class CommentForm(FlaskForm):
    author = StringField('名称', validators=[DataRequired(), Length(1, 30)])
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 254)])
    site = StringField('网址', validators=[Optional(), URL(), Length(0, 255)])
    body = TextAreaField('评论', validators=[DataRequired()])
    submit = SubmitField('发表评论')


# 管理员评论表单
class AdminCommentForm(FlaskForm):
    author = HiddenField()
    email = HiddenField()
    site = HiddenField()