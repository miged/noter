from noter import bcrypt, db
from sqlalchemy.ext.hybrid import hybrid_property
import datetime


class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    body = db.Column(db.Unicode)
    post_date = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, user, post_date=None):
        self.title = title
        self.body = body
        self.user_id = user
        if post_date is None:
            self.post_date = datetime.date.today()

    def __repr__(self):
        return '<title %r>' % self.title


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    _password = db.Column(db.String(128))

    def __init__(self, user, passw):
        self.username = user
        self._password = bcrypt.generate_password_hash(passw)
