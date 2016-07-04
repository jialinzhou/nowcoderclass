#   -*- encoding=UTF-8 -*-

from flask import  Flask
from flask_sqlalchemy import  SQLAlchemy

app = Flask(__name__)
app.config.from_pyfile('app.conf')
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
db = SQLAlchemy(app)
app.secret_key='ligaofeng'

from nowstagram import  views,models