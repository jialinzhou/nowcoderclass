#   -*- encoding=UTF-8 -*-
import random
from datetime import  datetime
from nowstagram import db


class User(db.Model):
    # id = db.column(db.Integer, primary_key=True, autoincremet=True)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(32))
    head_url = db.Column(db.String(256))
    image =  db.relationship('Images')

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.head_url = 'http://images.nowcoder.com/head/' + str(random.randint(0, 1000)) + 't.png'

    def __repr__(self):
        return '<User %d %s>' % (self.id, self.username)


class Images(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    url = db.Column(db.String(512))
    # comment = db.Column(db.String(1024))
    created_date = db.Column(db.DateTime)
    # comments = db.relationship('Comment')

    def __init__(self, url, user_id):
        self.url = url
        self.user_id = user_id
        self.created_date = datetime.now()

    def __repr__(self):
        return '<Images %s %d>' % (self.url, self.user_id)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer)
    content = db.Column(db.String(1024))
    image_id = db.Column(db.Integer)
    status = db.Column(db.Integer, default=0)
    # user =  db.relationship('User')

    def __init__(self, user_id, content, image_id):
        self.user_id = user_id
        self.content = content
        self.image_id = image_id
        # self.status = status

    def __repr__(self):
        return  '<Comment %s %d>' % (self.content, self.user_id)
