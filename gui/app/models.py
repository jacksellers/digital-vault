from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True, unique=True)
    last_name = db.Column(db.String(64), index=True, unique=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    balances = db.relationship('Balance', backref='client', lazy='dynamic')

    def __repr__(self):
        users = User.query.all()
        all_account_infos = []
        for u in users:
            user_account_info = [u.id, u.first_name, u.last_name, u.username]
            all_account_infos.append(user_account_info)
        return all_account_infos

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Balance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    balance_btc = db.Column(db.Float, index=True, unique=True)
    balance_usd = db.Column(db.Float, index=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Balance (BTC): {}, Balance (USD): {}>'.format(
            self.balance_btc, self.balance_usd)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
