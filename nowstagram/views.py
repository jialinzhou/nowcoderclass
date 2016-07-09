#   -*- encoding=UTF-8 -*-
from nowstagram import app, db,mail
from nowstagram.models import  User, Images ,Comment
from flask import  render_template,redirect,flash,get_flashed_messages,request
from flask_login import  login_user,logout_user,current_user,login_required
import  hashlib,random,json
from flask_mail import  Message

@app.route('/')
@app.route('/index/')
def index():
    images = Images.query.order_by(db.desc('id')).limit(10).all()
    # comments = Comment.query.filter_by('image_id=i')
    # for image in images:
    #     print image.comments
    return  render_template('index.html', images=images)

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


@app.route('/image/<int:image_id>/')
def Image(image_id):
    image = Images.query.get(image_id)
    if image == None:
        return  redirect('/')
    return render_template('pageDetail.html',image=image)

@app.route('/reloginpage/')
def reloginpage(msg=''):
    for m in get_flashed_messages(with_categories=False,category_filter=['relogin']):
        msg = msg + m
    return render_template('login.html',msg=msg, next=request.values.get('next'))


def redirect_with_msg(target,msg,category):
    flash(msg,category=category)
    return redirect(target)

@app.route('/reg/',methods={'get','post'})
def reg():
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()

    if username=='' or  password=='':
        return redirect_with_msg('/reloginpage/',u'用户名或密码不能为空','relogin')

    user = User.query.filter_by(username=username).first()
    if user != None:
        return  redirect_with_msg('/reloginpage/',u'用户名已存在','relogin')

    salt = '.'.join(random.sample('0123456789qbcdefghijklmnopqrstuvwxyz',10))
    m = hashlib.md5()
    m.update(password+salt)
    password = m.hexdigest()
    # temp_number = random.sample('01234567899876543210',4)
    # active_number = ''
    # for number in temp_number:
    #     active_number = active_number + number

    user = User(username, password, salt)
    db.session.add(user)
    db.session.commit()

    login_user(user)
    sender = ['gao_feng_li0@sina.com']
    recipients = [user]
    msg = 'http://127.0.0.1:5000/active/'+str(user.id)+'/'
    send_email('Nowstagram注册验证',sender,recipients,msg)
    next = request.values.get('next').strip()
    if next != None and next.startswith('/'):
        return redirect(next)
    return redirect('/')

@app.route('/active/<int:user_id>/')
def active_user(user_id):
    user = User.query.get(user_id)
    if user == None:
        return  'Fial to ative user!'
    if user.active == True:
        return  'User is actived before!'
    user.active = True
    db.session.commit()
    login_user(user)
    next = '/profile/'+str(user.id)+'/'
    return redirect(next)

@app.route('/login/', methods={'get', 'post'})
def login():
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()

    if username == '' or password == '':
        return redirect_with_msg('/reloginpage/', u'用户名或密码不能为空', 'relogin')

    user = User.query.filter_by(username=username).first()

    if user == None:
        return  redirect_with_msg('/reloginpage/',u'用户名不存在','relogin')

    m = hashlib.md5()
    m.update(password+user.salt)

    if m.hexdigest() != user.password:
        return redirect_with_msg('/reloginpage/', u'密码错误', 'relogin')

    if user.is_active():
        login_user(user)
        next = request.values.get('next').strip()
        if next != None and next.startswith('/'):
            return  redirect(next)
        return redirect('/')
    return 'Please active by your email!'

@app.route('/logout/')
def logout():
    logout_user()
    return  redirect('/')

def send_email(subject, sender, recipients, text_body, html_body=''):
    # if sender == None:
    #     sender = MAIL_DEFAULT_SENDER
    msg = Message(subject, sender, recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)

@app.route('/mail/')
def send_mail():
    authentication_number = random.sample('0123456789',4)
    sender = ['gao_feng_li0@sina.com']
    recipients = ['li-gao-feng@qq.com','gao_feng_li0@sina.com']
    text_body = 'the authenticated number is '+str(authentication_number)+'\n'+'please enter http://127.0.0.1:5000/ to finish authention'
    send_email(subject='Nowstagram注册验证',
               sender=sender,
              recipients=recipients,
               text_body=text_body
               )
    return  redirect('/')