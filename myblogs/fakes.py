from faker import Faker
import random

from myblogs.models import Admin, Category, Post, Comment
from myblogs.extensions import db


fake = Faker('zh_CN')

# 生成虚拟管理员信息
def fake_admin():
    admin = Admin(
        username = '管理员',
        blog_title = 'Blogs',
        blog_sub_title = "No,I'm the real thing.",
        name = '博客管理员',
        about = 'Hello everyone'
    )
    db.session.add(admin)
    db.session.commit()

# 创建虚拟分类
def fake_categories(count=10):
    category = Category(name='Default')
    db.session.add(category)

    for i in range(count):
        category = Category(name=fake.word())
        db.session.add(category)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback
'''
这个函数首先会创建一个默认分类， 默认分类是创建文章时默认设置的分类，然后依次生成包含随即名称的虚拟分类。
分类的名称要求不能重复，如果随机生成的分类名和以创建的分类重名，会抛出sqlalchemy.exc.IntegrityError
异常，此时调用db.session.rollback()方法进行回滚操作。
'''


# 生成虚拟文章 默认生成50篇文章，每一篇文章均指定了一个随即分类。
def fake_posts(count=50):
    for i in range(count):
        post = Post(
            author=fake.name(),
            title=fake.sentence(),
            body=fake.text(2000),
            category=Category.query.get(random.randint(1, Category.query.count())),
            timestamp=fake.date_time_this_year()
        )
        db.session.add(post)
    db.session.commit()


# 生成虚拟评论 随机生成200条评论， 另外再额外添加40条未审核评论 40条管理员评论和40条回复。
def fake_comments(count=200):
    for i in range(count):
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)

    salt = int(count * 0.2)
    for i in range(salt):
        # 未审核评论
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=False,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)

        #管理员发表的评论
        comment = Comment(
            author='博客管理员',
            email='liyuquanmail@163.com',
            site='jadespring.com',
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            from_admin=True,
            reviewed=True,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)
    db.session.commit()
    
    # 回复
    for i in range(salt):
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,
            replied=Comment.query.get(random.randint(1, Comment.query.count())),
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)
    db.session.commit()
        
