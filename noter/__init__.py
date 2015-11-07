import sqlite3
from flask import Flask, g
#from flask.ext.misaka import Misaka
from contextlib import closing

app = Flask(__name__)
app.config.from_pyfile('../config.cfg')
#Misaka(app)

# Connects to the database
def connect_db():
    con = sqlite3.connect(app.config['DATABASE'])
    return con

# Initializes the database
def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

import noter.views

if __name__ == '__main__':
    app.run()
