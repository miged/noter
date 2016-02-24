from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config.from_pyfile('../config.cfg')
db = SQLAlchemy(app)
db.create_all()

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    text = db.Column(db.Text)
    date = db.Column(db.DateTime)

    def __init__(self, title, text, post_date=None):
        self.title = title
        self.text = text
        if post_date is None:
            post_date = datetime.utcnow()

    def __repr__(self):
        return '<title %r>' % self.title

import noter.views

if __name__ == '__main__':
    db.create_all()
    app.run()
