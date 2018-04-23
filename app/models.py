from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from app import db, login
from hashlib import md5


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    balances = db.relationship('Balance', backref='client', lazy='dynamic')

    def __repr__(self):
        return '{}: {} {} @{}'.format(
            self.id, self.first_name, self.last_name, self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Balance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    balance_btc = db.Column(db.Float, index=True)
    balance_usd = db.Column(db.Float, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '{}: Balance (BTC): {}, Balance (USD): {}'.format(
            self.id, self.balance_btc, self.balance_usd)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    currency = db.Column(db.String(64), index=True)
    tx_type = db.Column(db.String(64), index=True)
    amount = db.Column(db.Float, index=True)
    price = db.Column(db.Float, index=True)
    tx_id = db.Column(db.Integer, index=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '{}: Timestamp: {}, Type: {}, Currency: {}, Amount: {}'.format(
            self.id, self.timestamp, self.tx_type,
            self.ccy, self.amount)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
