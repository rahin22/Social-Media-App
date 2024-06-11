from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String) 
    username = db.Column(db.String(12), unique=True)
    password = db.Column(db.String(100))
    email = db.Column(db.String, unique=True)
    dob = db.Column(db.String)
    bio = db.Column(db.String)
    pfp = db.Column(db.LargeBinary)
    gender = db.Column(db.String)


class followers(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    user = db.relationship('users', foreign_keys=[user_id])
    follower = db.relationship('users', foreign_keys=[follower_id])


class posts(db.Model):
    postID = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('users.id'))
    desc = db.Column(db.String)
    img = db.Column(db.String, unique=True)
    date = db.Column(db.String)

    user = db.relationship('users', backref='posts')


class likes(db.Model):
    postID = db.Column(db.Integer, db.ForeignKey('posts.postID'), primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    user = db.relationship('users', foreign_keys=[userID])
    post = db.relationship('posts', foreign_keys=[postID])


class comments(db.Model):
    commentID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    postID = db.Column(db.Integer, db.ForeignKey('posts.postID'))
    userID = db.Column(db.Integer, db.ForeignKey('users.id'))
    comment = db.Column(db.String)
    date = db.Column(db.String)

    post = db.relationship('posts', backref='comments')
    user = db.relationship('users', backref='comments')


class saved(db.Model):
    postID = db.Column(db.Integer, db.ForeignKey('posts.postID'), primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    user = db.relationship('users', foreign_keys=[userID])
    post = db.relationship('posts', foreign_keys=[postID])


class conversation(db.Model):
    conversationID = db.Column(db.Integer, primary_key=True)
    userID1 = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    userID2 = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    dateCreated = db.Column(db.String)
    lastUpdated = db.Column(db.String)
    
    user1 = db.relationship('users', foreign_keys=[userID1])
    user2 = db.relationship('users', foreign_keys=[userID2])

class message(db.Model):
    messageID = db.Column(db.Integer, primary_key=True)
    conversationID = db.Column(db.Integer, db.ForeignKey('conversation.conversationID'), nullable=False)
    senderID = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.String, nullable=False)
    date = db.Column(db.String)
    
    conversation = db.relationship('conversation', back_populates='message')
    sender = db.relationship('users')

conversation.message = db.relationship('message', order_by=message.date, back_populates='conversation')


class notifications(db.Model):
    notificationID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userID = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    notifyingUser = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.String, nullable=False)
    date = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)

    user = db.relationship('users', foreign_keys=[userID])
    user_notifying = db.relationship('users', foreign_keys=[notifyingUser])
