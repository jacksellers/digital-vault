from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True, unique=True)
    last_name = db.Column(db.String(64), index=True, unique=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(256))
    balances = db.relationship('Balance', backref='client', lazy='dynamic')

    def __repr__(self):
        return '<User: {} {}>'.format(self.first_name, self.last_name)


class Balance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    balance_btc = db.Column(db.Float, index=True, unique=True)
    balance_usd = db.Column(db.Float, index=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Balance (BTC): {}, Balance (USD): {}>'.format(
            self.balance_btc, self.balance_usd)
