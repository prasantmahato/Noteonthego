from datetime import datetime
from enum import unique
from app import app, db, login

from time import time
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5

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
    about_me = db.Column(db.String(64), nullable=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    notes = db.relationship('Todo', backref='author', lazy='dynamic')
    
    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

        
    def avatar(self, profile_image, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d={}&s={}'.format(digest,profile_image, size)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))