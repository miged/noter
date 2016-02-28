from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
db = SQLAlchemy(app)
app.config.from_pyfile('../config.cfg')

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    body = db.Column(db.Unicode)
    post_date = db.Column(db.Text)

    def __init__(self, title, body, post_date=None):
        self.title = title
        self.body = body
        if post_date is None:
            self.post_date = datetime.date.today()

    def __repr__(self):
        return '<title %r>' % self.title

db.create_all()
import noter.views

if __name__ == '__main__':
    app.run()
