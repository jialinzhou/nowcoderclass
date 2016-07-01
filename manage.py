#   -*- encoding=UTF-8 -*-
import  random
from  nowstagram import  app, db
from nowstagram.models import  User, Images, Comment
from  flask_script import  Manager
# import  operator

manager = Manager(app)

def get_url():
    return 'http://images.nowcoder.com/head/' + str(random.randint(0, 1000)) + 'm.png'

# 这里是用命令行来运行的，和服务器是异步的，如果不运行命令行更新数据库，再怎么重启服务器都是不会改变数据的
@manager.command
def init_database():
    db.drop_all()
    db.create_all()
    for i in range(0, 100):
        db.session.add(User('practice'+str(i+1), 'pass'+str(i+1)))
    #   密码是需要加密的
        for j in range(0, 3):
            db.session.add(Images(get_url(), i))
            for k in range(0, 3):
                # db.session.add(Comment('这是一条评论'+str(k), random.randint(0,100),random.randint(0,100)))
                db.session.add(Comment('this is a comment'+str(k+1), i,  1 + 3 * i + j,))
#                 需要将中文字符串转换成 buffer() 类型才不会有问题
#                 sqlite3针对BLOB（二进制大对象）的存储时默认为buffer类型的，所以需要进行转换
#                 可是这样数据库里面显示的就不是中文了啊
#             出现中文的字符会出错，错误提示如下：
# You must not use 8-bit bytestrings unless you use a text_factory that can interpret 8-bit bytestrings (like text_factory = str). It is highly recomme
# nded that you instead just switch your application to Unicode strings. [SQL: u'INSERT INTO comment (user_id, content, image_id, status) VALUES (?, ?, ?, ?)'] [parameters: ('\xe8\xbf\x99this is a comment', 4, 2
# , 1)]
#             即这个数据库的字符串不支持中文字符
    db.session.commit()

    for i in range(0, 100, 2):
        User.query.filter_by(id=i+1).update({'username':'prac'+str(i+1)})
    # 这个确实更新了数据库，通过query查询到的数据时更新了的，但是用数据库打开却看不到更新，不知道为什么
    # 因为没有提交commit，哈哈哈哈哈
    db.session.commit()

    # for i in range(0, 100, 3):
    #     p = User.query.get(i+1)
    #     p.username = 'u'+str(i+1)
    #     # 通过属性设置会出错？错误描述： 'NoneType' object has no attribute 'username'
    #     #为什么识别为 NONETYPE ？
    # db.session.commit()

    # for i in range(0,50,3):
    #     User.query.filter_by(id=i+2).delete()
    # #     直接对查询的到结果进行删除
    # for i in range(50,100,4):
    #     comment =Comment.query.filter_by(id=i+1).first()
    #     # comment = Comment.query.get(i)
    #     # 对查询到的结果进行会话删除，删除对象每次只能提交一个，不能提交多个
    #     # filter_by()得到的结果是一个列表，虽然这个列表可能只有一个元素，但仍然通不过 .first()则提交的不是列表了
    #     db.session.delete(comment)
    # db.session.commit()


    print 1, User.query.all( )
    print 2, User.query.get(10)
    print 3, User.query.filter_by(id=5).first()
    print 4, User.query.order_by(User.id.desc()).offset(1).limit(4).all()
    print 5, User.query.paginate(page=2, per_page=10).items
    # 分页显示
    # print 5, User.query.filter(or_(User.id== 3,User.id == 88)).all()
    #or_ and_ 这些组合操作符否不可用，不知从哪里导入
    u = User.query.get(7)
    print 6,u.username
    #为何这边却可以这样用呢？还是因为名字冲突了，不是名称的问题啊
    #一对多查询
    # print  7, u.comment
    print  72,u.images.all()
    # 在没有设置backref的情况下，可以正确的得到关联的images结果，但backref后就没有了
    # 有结果，但是直接打印出出来格式不对，用.all()就可以全部打印出来
    print 88,Images.query.get(8).user.id
    print 89,Images.query.order_by(db.desc('images.id')).limit(10).first()
    images = Images.query.order_by(db.desc('images.id')).limit(10).all()
    for image in images:
        # print 8, image.user.id, image.user.head_url, image.user.username
        print  8,image.id,image.comment
#     为什么可以进行反向查询但是，在Html里面就是不行呢？
#     为什么结果显示仍然为空？因为查询的哪一项不存在，被前面删除了
#     c = Comment.query.get(7)
#     print 9, c
#     # print 10, c.user
#     print  11,c.image_id

if __name__ == '__main__':
    manager.run()