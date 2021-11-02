from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'usertable'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15))
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(256))


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usertable.id'))
    user = db.relationship('User')

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category')

    title = db.Column(db.String(256))
    description = db.Column(db.Text())
    price = db.Column(db.Float())
    date_time = db.Column(db.DateTime())
    status = db.Column(db.String(50))
    image_link = db.Column(db.String(256))
    total_tickets = db.Column(db.Integer())
    location = db.Column(db.String(256))


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer(), db.ForeignKey('usertable.id'))
    user = db.relationship('User')

    event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    event = db.relationship('Event')

    quantity = db.Column(db.Integer())


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(256))


class Comment(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("usertable.id"))
    user = db.relationship("User")

    event_id = db.Column(db.Integer(), db.ForeignKey("event.id"))
    comment = db.Column(db.Text())
    created_on = db.Column(db.DateTime(), default=func.now())
