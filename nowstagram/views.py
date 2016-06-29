#   -*- encoding=UTF-8 -*-

from nowstagram import app

@app.route('/index')
def index():
    return 'hello'