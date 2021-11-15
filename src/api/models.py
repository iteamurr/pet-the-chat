"""
    This module is responsible for the representation of models in the database.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model in the database."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)


class Room(db.Model):
    """Room model in the database."""

    __tablename__ = "rooms"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    chat_link = db.Column(db.String(50), nullable=False)


class Chat(db.Model):
    """Chat model in the database."""

    __tablename__ = "chats"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), nullable=False)
    link = db.Column(db.String(50), unique=True, nullable=False)
