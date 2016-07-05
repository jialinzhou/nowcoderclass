#   -*- encoding=UTF-8 -*-

from flask import  Flask
from flask_sqlalchemy import  SQLAlchemy
from flask_login import  LoginManager

app = Flask(__name__)
app.config.from_pyfile('app.conf')
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = '/reloginpage/'
app.secret_key = 'ligaofeng'

from nowstagram import  views,models