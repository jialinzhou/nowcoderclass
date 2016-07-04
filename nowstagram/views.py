#   -*- encoding=UTF-8 -*-
from nowstagram import app, db
from nowstagram.models import  User, Images ,Comment
from flask import  render_template,redirect,request,flash,get_flashed_messages
import  random,hashlib

@app.route('/')
@app.route('/index')
def index():
    images = Images.query.order_by(db.desc('id')).limit(10).all()
    # comments = Comment.query.filter_by('image_id=i')
    for image in images:
        print image.comments
    return  render_template('index.html', images=images)

@app.route('/profile/<int:user_id>/')
def profile(user_id):
    user = User.query.get(user_id)
    if user == None:
        return  redirect('/')
    return  render_template('profile.html',user=user)

@app.route('/image/<int:image_id>/')
def Image(image_id):
    image = Images.query.get(image_id)
    if image == None:
        return  redirect('/')
    return render_template('pageDetail.html',image=image)

@app.route('/reloginpage/')
def login(msg=''):
    # 这个函数需要接收一个参数
    for m in get_flashed_messages(with_categories=False,category_filter=['relogin']):
        msg = m+msg
    # msg = get_flashed_messages(with_categories=False,category_filter=['relogin'])
    # get_flashed_message接收的是一个元组，而不是一个字符串，故而直接传过去会显示为 [ ]胃不是字符
    return  render_template('login.html',msg=msg)

def redirct_with_msg(target,msg,category):
    if msg != None:
        flash(msg,category=category)
        return  redirect(target)

# 为什么根本不会跳转到这个地方来啊，表单提交到这里的啊
# 为什么会一直跳转在注册页，完全不合理啊   代码有点问题 多了一个 ;
@app.route('/reg/',methods={'post','get'})
def reg():
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()

    if username == '' or password == '':
        return redirct_with_msg('/reloginpage/', u'用户名或密码不能为空', 'relogin')

    user = User.query.filter_by(username=username).first()
    if user != None:
        return  redirct_with_msg('/reloginpage/', u'用户名已经存在', 'relogin')

    salt='.'.join(random.sample('0123456789abcdefghijklmnopqrstuvwxyz', 10))
    m = hashlib.md5()
    m.update(password+salt)
    password = m.hexdigest()

    user = User(username, password, salt)
    db.session.add(user)
    db.session.commit()

    return  redirect('/')


#  更多判断

