from datetime import datetime
from enum import unique
from app import app, db, login

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

#   Defining Database
class Todo(db.Model):
   id = db.Column(db.Integer, primary_key = True)
   content = db.Column(db.String(200),nullable=False)
   date_created = db.Column(db.DateTime, default=datetime.utcnow)
   user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

   def __repr__(self):
       return '<Task %r>' % self.id

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    notes = db.relationship('Todo', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))