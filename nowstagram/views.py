#   -*- encoding=UTF-8 -*-
from nowstagram import app, db
from nowstagram.models import  User, Images ,Comment
from flask import  render_template,redirect

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