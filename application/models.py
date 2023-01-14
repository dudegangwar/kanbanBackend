from .database import db
from dataclasses import dataclass
from flask_login import login_manager
# from flask_security import UserMixin, RoleMixin
from sqlalchemy.sql import func
from datetime import datetime


#-------------Model-----------------------------
# roles_users = db.Table('roles_users',
#         db.Column('user_id', db.Integer(), db.ForeignKey('user_id')),
#         db.Column('role_id', db.Integer(), db.ForeignKey('role_id')))

@dataclass
class Users(db.Model):
    id: int
    name: str
    email: str
    password: str
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String)

@dataclass
class List(db.Model):
    id: int
    listname: str
    userid:int
    created_at: str
    updated_at: str

    id = db.Column(db.Integer, primary_key=True)
    listname = db.Column(db.String)
    userid = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)

@dataclass
class Tasks(db.Model):
    id: int
    title: str
    content: str
    deadline: str
    flag: int
    parent: int
    userID: int
    lastUpdate:str
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    content = db.Column(db.String)
    deadline = db.Column(db.String)
    flag = db.Column(db.Integer)
    parent = db.Column(db.Integer)
    userID = db.Column(db.Integer)
    lastUpdate = db.Column(db.DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)
