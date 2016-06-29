#   -*- encoding=UTF-8 -*-
import  random
from  nowstagram import  app,db
from nowstagram.models import  User,Images,Comment
from  flask_script import  Manager

manager = Manager(app)

def get_url():
    return 'http://images.nowcoder.com/head/' + str(random.randint(0, 1000)) + 'm.png'

@manager.command
def init_database():
    db.drop_all()
    db.create_all()
    for i in range(1, 100):
        db.session.add(User("practice"+str(i), 'pass'+str(i)))
    #   密码是需要加密的
        for j in range(0, 3):
            db.session.add(Images(get_url(), i+1))
            for k in range(0, 3):
                # db.session.add(Comment('这是一条评论', random.randint(0,100),random.randint(0,100)))
                db.session.add(Comment('this is a comment', 1 + 3 * i + j, i + 1))
#             出现中文的字符会出错，错误提示如下：
# You must not use 8-bit bytestrings unless you use a text_factory that can interpret 8-bit bytestrings (like text_factory = str). It is highly recomme
# nded that you instead just switch your application to Unicode strings. [SQL: u'INSERT INTO comment (user_id, content, image_id, status) VALUES (?, ?, ?, ?)'] [parameters: ('\xe8\xbf\x99this is a comment', 4, 2
# , 1)]
#             即这个数据库的字符串不支持中文字符

    db.session.commit()

if __name__ == '__main__':
    manager.run()