# This is where you define the models of your application.
# This may be split into several modules in the same way as views.py

# datetime.fromtimestamp(time.time())

import jwt

from datetime import date
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)


db = SQLAlchemy()
auth = HTTPBasicAuth()
bcrypt = Bcrypt()

roles_users = db.Table(
    'roles_user',
    db.Column('user_id', db.Integer(), db.ForeignKey('User.user_id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('Role.role_id'))
)


class Role(db.Model):

    __tablename__ = 'Role'

    role_id = db.Column(db.Integer(), primary_key=True)
    role_name = db.Column(db.String(20), unique=True)
    description = db.Column(db.String(50))

    def __init__(self, role_name):
        self.role_name = role_name

    def __repr__(self):
        return '<Role %r>' % (self.role_name)


class User(db.Model):

    __tablename__ = 'User'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    authenticated = db.Column(db.Boolean, nullable=False, default=False)
    active = db.Column(db.Boolean, nullable=False, default=False)
    roles = db.Column(db.String(5), nullable=False)
    created_on = db.Column(db.DateTime, default=date.today().isoformat())

    def __init__(self, username, email, password, roles):
        self.username = username
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, app.config.get('BCRYPT_LEVEL')
            ).decode()
        self.authenticated = False
        self.active = False
        self.roles = roles

    def __repr__(self):
        return '<User %r>' % (self.username)

    def get_id(self):
        """Return username to satisfy Flask-Login's requirements"""
        return self.username

    def is_authenticated(self):
        """Return True if the user is authenticated"""
        return self.authenticated

    def is_active(self):
        """Return if user has activated their account"""
        return self.active

    def is_anonymous(self):
        """False, as anonymous users aren't supported"""
        return False

    @auth.verify_password
    def verify_password(password):
        if bcrypt.check_password_hash(self.password, password):
            return True

        return False

    def generate_auth_token(self, expiration=60 * 60):
        s = Serializer(
            secret_key=app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'user_id': self.user_id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(secret_key=app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            # valid token, but expired
            return None
        except BadSignature:
            # invalid token
            return None
        user = User.query.get(data['user_id'])
        return user

    def encode_auth_token(self, user_id):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=5),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'


class Bucketlist(db.Model):

    __tablename__ = 'Bucketlist'

    list_id = db.Column(db.Integer, primary_key=True)
    list_name = db.Column(db.String(20), unique=True, nullable=False)
    is_completed = db.Column(db.Boolean(), nullable=False, default=False)
    created_on = db.Column(db.DateTime, default=date.today().isoformat())
    date_modified = db.Column(db.DateTime, default=date.today().isoformat())
    created_by = db.Column(db.Integer, db.ForeignKey('User.user_id'))

    def __init__(self, list_name, created_by):
        self.list_name = list_name
        self.created_by = created_by

        self.is_completed = False
        self.created_on = date.today().isoformat()
        self.date_modified = date.today().isoformat()

    def __repr__(self):
        """Return Bucketlist name"""
        return '<Bucketlist %r>' % (self.list_name)

    def get_id(self):
        """Return Bucketlist id"""
        return self.list_id

    def list_is_completed(self):
        """Return True if the all bucketlist items have been completed"""
        return self.is_completed


class Bucketlist_Item(db.Model):

    __tablename__ = 'Bucketlist_Item'

    item_id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('Bucketlist.list_id'))
    item_name = db.Column(db.String(20), unique=True, nullable=False)
    is_completed = db.Column(db.Boolean(), nullable=False, default=False)
    created_on = db.Column(db.DateTime, default=date.today().isoformat())
    date_modified = db.Column(db.DateTime, default=date.today().isoformat())

    def __init__(self, item_name, list_id):
        self.item_name = item_name
        self.list_id = list_id

        self.is_completed = False
        self.created_on = date.today().isoformat()
        self.date_modified = date.today().isoformat()

    def __repr__(self):
        """Return Bucketlist item name"""
        return '<Bucketlist %r>' % (self.list_name)

    def get_id(self):
        """Return Bucketlist item id"""
        return self.item_id

    def list_is_completed(self):
        """Return True if item has been completed"""
        return self.is_completed