#   -*- encoding=UTF-8 -*-
from nowstagram import app, db,mail
from nowstagram.models import  User, Images ,Comment
from flask import  render_template,redirect,flash,get_flashed_messages,request,send_from_directory
from flask_login import  login_user,logout_user,current_user,login_required
import  hashlib,random,json,base64,os,uuid
from flask_mail import  Message
from datetime import  datetime,date
from qiniusdk import qiniu_upload

@app.route('/')
@app.route('/index/')
def index():
    # images = Images.query.order_by(db.desc('id')).limit(10).all()
    paginate = Images.query.order_by(db.desc('priority')).order_by(db.desc('pv')).order_by(db.desc('id')).paginate(page=1,per_page=10,error_out=False)
    # comments = Comment.query.filter_by('image_id=i')
    # for image in images:
    #     print image.comments
    return  render_template('index.html', images=paginate.items, has_next=paginate.has_next )

@app.route('/profile/<int:user_id>/')
@login_required
def profile(user_id):
    user = User.query.get(user_id)
    if user == None:
        return  redirect('/')
    paginate  = Images.query.filter_by(user_id=user_id).paginate(page=1, per_page=3, error_out=False)
    return  render_template('profile.html', user=user, images=paginate.items,has_next=paginate.has_next)

@app.route('/profile/images/<int:user_id>/<int:page>/<int:per_page>/')
def user_image(user_id,page,per_page):
    paginate = Images.query.filter_by(user_id=user_id).paginate(page=page, per_page=per_page, error_out=False)
    map = {'has_next':paginate.has_next}
    images = []
    for image in paginate.items:
        imgvo = {'id':image.id, 'url':image.url,'comment_count':len(image.comments)}
        images.append(imgvo)

    map['images']=images
    return json.dumps(map)

# 解决json 中 datetime无法序列化的问题，扩展一个CJsonEncoder
# 然后在json.dumps( ,cls=CJsonEncoder) 加上 cls 参数即可，解析也完全不用操心
class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)

@app.route('/index/<int:page>/<int:per_page>/')
def index_more(page,per_page):
    paginate = Images.query.order_by(db.desc('priority')).order_by(db.desc('pv')).order_by(db.desc('id')).paginate(page=page,per_page=per_page,error_out=False)
    map = {'has_next':paginate.has_next}
    images = []
    for image in paginate.items:
        comment_username=[]
        comment_user_id=[]
        comment_content=[]
        for i in range(0,min(2,len(image.comments))):
            comment = image.comments[i]
            comment_username.append(comment.user.username)
            comment_user_id.append(comment.user_id)
            comment_content.append(comment.content)
            # comments.append({'comment_username': comment.user.username,
            #                  'comment_user_id': comment.user_id,
            #                   'content': comment.content})
        # 评论可以组成数组 当做json的一个对象传过去，可找不到解析的方法，故而仅传一个评论吧！
        imgvo = {'image_id':image.id,
                 'image_url':image.url,
                 'image_comments_length':len(image.comments),
                 'created_date':image.created_date,
                 'image_user_id':image.user.id,
                 'image_user_head_url':image.user.head_url,
                 'image_user_username':image.user.username,
                 'comment_user_username':comment_username,
                 'comment_user_id':comment_user_id,
                 'comment_content':comment_content}
        images.append(imgvo)

    map['images']=images
    return json.dumps(map,cls=CJsonEncoder)

@app.route('/image/<int:image_id>/')
def Image(image_id):
    image = Images.query.get(image_id)
    if image == None:
        return  redirect('/')
    image.pv = image.pv + 1
    db.session.commit()
    return render_template('pageDetail.html',image=image)

@app.route('/loginpage/')
def reloginpage(msg=''):
    for m in get_flashed_messages(with_categories=False,category_filter=['login']):
        msg = msg + m
    return render_template('login.html',msg=msg, next=request.values.get('next'))

@app.route('/regpage/')
def register(msg=''):
    for m in get_flashed_messages(with_categories=False, category_filter=['reg']):
        msg = msg + m
    return render_template('register.html', msg=msg, next=request.values.get('next'))

def redirect_with_msg(target,msg,category):
    flash(msg,category=category)
    return redirect(target)

@app.route('/register/',methods={'get','post'})
def reg():
    # print request.values.get('email')
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()
    password_again = request.values.get('password_again').strip()
    email = request.values.get('email')
    # print  email

    if username=='' or  password=='' or email=='' or password_again=='':
        return redirect_with_msg('/regpage/',u'用户名或密码或邮箱不能为空','reg')

    if '@' not in email or '.' not in email:
        return  redirect_with_msg('/regpage/',u'请使用正确邮箱地址注册','reg')

    if password != password_again:
        return  redirect_with_msg('/regpage/',u'两次输入密码不一致','reg')

    user = User.query.filter_by(username=username).first()
    if user != None:
        return  redirect_with_msg('/regpage/',u'用户名已存在','reg')

    eml = User.query.filter_by(email=email).first()
    if eml != None:
        return  redirect_with_msg('/regpage/',u'该邮箱已注册请登录','reg')

    salt = '.'.join(random.sample('0123456789qbcdefghijklmnopqrstuvwxyz',10))
    m = hashlib.md5()
    m.update(password+salt)
    password = m.hexdigest()
    user = User(username=username, password=password, salt=salt, email=email)
    db.session.add(user)
    db.session.commit()

    login_user(user, force=True)
    sender = 'gao_feng_li0@sina.com'
    recipients = [user.email]
    # 用base64对激活链接后面对用户进行识别的部分进行加密
    # user_id 太短了，所以还是用user.username进行加密更好一些
    text = 'Please enter the url below to active your account!\n'
    active_url = 'http://127.0.0.1:5000/active/' + base64.urlsafe_b64encode(str(user.email)).rstrip('=') + '/'
    msg = text + active_url
    send_email(subject='Nowstagram注册验证', sender=sender, recipients=recipients, text_body=msg)

    next = request.values.get('next').strip()
    if next != None and next.startswith('/'):
        return redirect(next)
    return redirect('/')

@app.route('/login/', methods={'get', 'post'})
def login():
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()

    if username == '' or password == '':
        return redirect_with_msg('/loginpage/', u'用户名或密码不能为空', 'login')

    if '@' in username and '.' in username:
        email = username
        user = User.query.filter_by(email=email).first()
        if user == None:
            return redirect_with_msg('/loginpage/', u'邮箱未注册', 'login')
        m = hashlib.md5()
        m.update(password + user.salt)
        if m.hexdigest() != user.password:
            return redirect_with_msg('/loginpage/', u'密码错误', 'login')
        print login_user(user,force=True)
        next = request.values.get('next').strip()
        if next != None and next.startswith('/'):
            return redirect(next)
        return redirect('/')
    user = User.query.filter_by(username=username).first()
    if user == None:
        return  redirect_with_msg('/loginpage/',u'用户名不存在','login')
    m = hashlib.md5()
    m.update(password+user.salt)
    if m.hexdigest() != user.password:
        return redirect_with_msg('/loginpage/', u'密码错误', 'login')
    print  login_user(user,force=True)
    # login_user(user) 会莫名其妙失败，返回false，这部分代码没改过，以前一直正常的
    next = request.values.get('next').strip()
    if next != None and next.startswith('/'):
        return  redirect(next)
    return redirect('/')

# 如此简单的激活方法肯定有问题
# 激活链接如何加密，如何解密？或者用伪静态url
# 可以使用base64进行加密，但只是对user_id进行加密
# base64加密解密使用方法示例
#  !/usr/bin/env python
#
# def base64_url_decode(inp):
#     # 通过url传输时去掉了=号，所以需要补上=号
#     import base64
#     return base64.urlsafe_b64decode(str(inp + '=' * (4 - len(inp) % 4)))
#
# def base64_url_encode(inp):
#     import base64
#     return base64.urlsafe_b64encode(str(inp)).rstrip('=')
@app.route('/active/<string:username_base64>/')
def active_user(username_base64):
    email = base64.urlsafe_b64decode(str(username_base64 + '=' * (4 - len(username_base64) % 4)))
    user = User.query.filter_by(email=email).first()
    if user == None:
        return  '用户不存在！'
    if user.active == True:
        return  '用户已处于激活态，请勿重复激活'
    user.active = True
    db.session.commit()
    login_user(user, force=True)
    next = '/profile/'+str(user.id)+'/'
    return redirect(next)

@app.route('/logout/')
def logout():
    logout_user()
    return  redirect('/')

def send_email(subject, sender, recipients, text_body, html_body=''):
    if sender == None:
        sender = app.conf['MAIL_DEFAULT_SENDER']
    msg = Message(subject=subject, sender=sender, recipients=recipients)
    # msg = Message(subject, sender, recipients) 这是错误的写法
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)

# 总结：msg = Message(subject=subject, sender=sender, recipients=recipients) 用法正确
#       msg = Message(subject, sender, recipients) 用法错误，该用法会使用默认发件人进行发件，如无设置默认发件人会提示出错
#       同时会将第二个sender参数解析成收件人，要求用列表[]格式，否则提示出错，如果按提示修改成列表格式后可以无措运行
#       但是从默认发件人发送到发件人，根本就没达到要求
@app.route('/mail/')
def send_mail():
    authentication_number = random.sample('0123456789',4)
    # sender = ['gao_feng_li0@sina.com']  错误写法
    sender = "gao_feng_li0@sina.com"
    recipients = ["18700946089@sina.cn","835757447@qq.com"]
    text_body = 'the authenticated number is '+str(authentication_number)+'\n'+'please enter http://127.0.0.1:5000/ to finish authention'
    send_email(subject='Nowstagram注册验证',
               sender=sender,
              recipients=recipients,
               text_body=text_body
               )
    return  redirect('/')

# test base64 encode and decode
# @app.route('/encode/')
# def encode():
#     inp = '/profile/102/'
#     jiami = base64.urlsafe_b64encode(str(inp)).rstrip('=')
#     jiemi = base64.urlsafe_b64decode(str(jiami + '=' * (4 - len(jiami) % 4)))
#     return jiemi

def save_to_local(file,filename):
    save_dir = app.config['UPLOAD_DIR']
    file.save(os.path.join(save_dir,filename))
    return '/image/'+filename

@app.route('/image/<image_name>')
def  view_image(image_name):
    return  send_from_directory(app.config['UPLOAD_DIR'],image_name)


@app.route('/upload/',methods={'post'})
def upload():
    file = request.files['file']
    ext_name = file.filename.rsplit('.',1)[1].strip().lower()
    if ext_name in app.config['ALLOWED_EXT']:
        file_name = str(uuid.uuid1()).replace('-','')+'.'+ext_name
        # url = save_to_local(file,file_name)
        url = qiniu_upload(file,file_name)
        if url != None:
            db.session.add(Images(url,current_user.id))
            db.session.commit()
    return  redirect('/profile/%d' %current_user.id)

@app.route('/addcomment/',methods={'post'})
def add_comment():
    if current_user.is_authenticated:
        # print current_user.is_authenticated
        if current_user.is_active:
            # print  current_user.is_active
            image_id = request.values.get('image_id')
            content = request.values.get('content')
            comment = Comment(image_id=image_id,content=content,user_id=current_user.id)
            db.session.add(comment)
            db.session.commit()
            return json.dumps({'code':0,
                               'id':comment.id,
                               'image_id':image_id,
                               'content':content,
                               'username':comment.user.username,
                               'user_id':comment.user_id})
        return json.dumps({'code':1,
                                'msg':"请完成激活后评论！"})
    return json.dumps({'code': 1,
                       'msg': "请登录后进行评论！"})

@app.route('/deleteimage/<int:image_id>/')
def delete_image(image_id):
    image = Images.query.get(image_id)
    if image != None:
        db.session.delete(image)
        db.session.commit()
        return  redirect('/')

@app.route('/deletecomment/<int:image_id>/<int:comment_id>/')
def delete_comment(image_id,comment_id):
    comment = Comment.query.get(comment_id)
    if comment != None:
        db.session.delete(comment)
        db.session.commit()
        return  redirect('/image/'+str(image_id) + '/')

@app.route('/priority/<int:image_id>/')
def priority_image(image_id):
    image = Images.query.get(image_id)
    if image != None:
        image.priority = image.priority + 1
        db.session.commit()
        return  redirect('/image/'+str(image_id) + '/')

@app.route('/quitpriority/<int:image_id>/')
def quitpriority_image(image_id):
    image = Images.query.get(image_id)
    if image != None:
        image.priority = 0
        db.session.commit()
        return  redirect('/image/'+str(image_id) + '/')
