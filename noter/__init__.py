from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
db = SQLAlchemy(app)
app.config.from_pyfile('../config.cfg')

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    body = db.Column(db.Unicode)
    date = db.Column(db.DateTime)

    def __init__(self, title, body, post_date=None):
        self.title = title
        self.body = body
        if post_date is None:
            post_date = datetime.utcnow()

    def __repr__(self):
        return '<title %r>' % self.title

db.create_all()
import noter.views

if __name__ == '__main__':
    app.run()
