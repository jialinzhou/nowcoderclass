#   -*- encoding=UTF-8 -*-
import random
from datetime import  datetime
from nowstagram import db,login_manager

# 关于一对多关系的解释举例：在User类中存在images属性与Images类关联起来，但是在User类创建时Images类
# 并不存在，也就是创建之间存在先后关系，在先创建的类User中使用images占位符来代替暂未创建的Images中的属性
# 在创建Images类时使用外键将user_id与User类关联起来，因为在User类中使用了db.relationship关联了Images，
# 故而可以用images属性查询Images表中的相关内容，而Images类并没有与User类用relationship关联，故而不能方向查询
# 但是在使用了backref后则可以反向查询User类中相关信息，查询关键字时backref=的那个

# 会自动将类名转换成小写然后作为表名，，，所以再外键时使用的是表名，而不是类名
#但可以通过  __tablename__ = 'myuser' 来指定表名字
class User(db.Model):
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    # id = db.column(db.Integer, primary_key=True, autoincremet=True)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 可以由多个主键
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(32))
    salt = db.Column(db.String(32))
    head_url = db.Column(db.String(256))
    comments = db.relationship('Comment',backref='user',lazy='dynamic')
    # images = db.relationship('Images')
    images =  db.relationship('Images', backref='user', lazy='dynamic')

    def __init__(self, username, password,salt=''):
        self.username = username
        self.password = password
        self.salt = salt
        self.head_url = 'http://images.nowcoder.com/head/' + str(random.randint(0, 1000)) + 't.png'

    def __repr__(self):
        return ('<User %d %s>' % (self.id, self.username)).encode('gbk')

    def is_authenticated(self):
        return  True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class Images(db.Model):
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # db.ForeignKey('user.id') 而不能是 'User.id' 否则会找不到，因为默认表名是类名的小写
    url = db.Column(db.String(512))
    # comment = db.Column(db.String(1024))
    created_date = db.Column(db.DateTime)
    comments = db.relationship('Comment')
    # comment = db.relationship('Comment', backref='images', lazy='dynamic')

    def __init__(self, url, user_id):
        self.url = url
        self.user_id = user_id
        self.created_date = datetime.now()

    def __repr__(self):
        return '<Images %s %d>' % (self.url, self.user_id)


class Comment(db.Model):
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    # 增加对中文的支持,可是我增加了这条之后仍然无法支持中文啊
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.String(1024))
    image_id = db.Column(db.Integer,db.ForeignKey('images.id'))
    status = db.Column(db.Integer, default=0)
    # user =  db.relationship('User')

    def __init__(self, content, user_id,  image_id):
        self.content = content
        self.user_id = user_id
        self.image_id = image_id

    def __repr__(self):
        return  ('<Comment %s %d>' % (self.content, self.user_id)).encode('gbk')
