from extentions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class Users(db.Model, UserMixin):

    username = db.Column(db.String(24), primary_key=True)
    password_hash = db.Column(db.String(128), nullable=False)
    last_password_change = db.Column(db.DateTime)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    date_added = db.Column(db.DateTime, nullable=False)

    permissions = db.relationship('Permissions', backref='owner', foreign_keys='Permissions.owner_username')
    permissions_given = db.relationship('Permissions', backref='giver', foreign_keys='Permissions.giver_username')

    def __init__(self, username: str, nome: str, email: str, password: str):
        self.username = username.upper()
        self.nome = nome
        self.email = email.lower()
        self.password = password
        self.date_added = datetime.now()

    def get_id(self):
        return self.username

    @property
    def password(self):
        raise AttributeError('Password is not readable attribute!')

    @password.setter
    def password(self, pswd):
        self.password_hash = generate_password_hash(pswd)

    def verify_password(self, pswd):
        return check_password_hash(self.password_hash, pswd)

    def has_permission(self, perm: str):
        perm = perm.lower()
        if self.is_authenticated:
            user_perms = []
            for p in self.permissions:
                user_perms.append(p.permission)
            if "*" in user_perms or perm in user_perms:
                return True
            else:
                perm_check = ""
                for s in perm.split(".")[:-1]:
                    perm_check += s + "."
                    if (perm_check + "*") in user_perms:
                        return True
        return False

    def __repr__(self):
        return f'<Username {self.username}>'


class Permissions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_username = db.Column(db.String(24), db.ForeignKey('users.username'))
    giver_username = db.Column(db.String(24), db.ForeignKey('users.username'))
    permission = db.Column(db.String(256), nullable=False)
    date_owned = db.Column(db.DateTime, nullable=False)

    def __init__(self, owner, giver, permission: str):
        self.owner_username = owner
        self.giver_username = giver
        self.permission = permission.lower()
        self.date_owned = datetime.now()
