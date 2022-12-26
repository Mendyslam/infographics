from hashlib import md5
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from app import db
from app import login

# User and Post association Table
follows = db.Table(
    'follows',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
)

class User(UserMixin, db.Model):
    """
    User model
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow())
    followed = db.relationship('User', secondary=follows, lazy='dynamic',
        primaryjoin=(follows.c.follower_id == id), secondaryjoin=(follows.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'))

    def set_password(self, password):
        """
        Hash user password
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Validate user password
        """
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        """
        User profile image
        """
        hashdigest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            hashdigest, size
        )

    def follow(self, user):
        """
        Adds user to instance followed list
        """
        if not self.following(user):
            self.followed.append(user)

    def unfollow(self, user):
        """
        Removes user from instance follwed list
        """
        if self.following(user):
            self.followed.remove(user)

    def following(self, user):
        """
        Checks if instance is following user
        """
        return self.followed.filter(
            follows.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        """
        Posts of instance and users followed by instance
        """
        followed_posts = Post.query.join(
            follows, (follows.c.followed_id == Post.user_id)).filter(follows.c.follower_id == self.id)
        instance_posts = Post.query.filter_by(user_id = self.id)
        return followed_posts.union(instance_posts).order_by(Post.timestamp.desc())

    def __repr__(self):
        """
        Representaion of a User instance
        """
        return '<User {}>'.format(self.username)


class Post(db.Model):
    """
    Post model
    """
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        """
        Representaion of a Post instance
        """
        return '<Post {}>'.format(self.body)


@login.user_loader
def loader_user(id):
    return User.query.get(int(id))
