from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
                    FloatField, RadioField
from app.blockchain import get_from_bitcoind, search_blockchain
from wtforms.validators import DataRequired
from flask import redirect, url_for
from flask_wtf import FlaskForm
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    login = SubmitField('Login')


class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    register = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('That username is taken')


class TradeForm(FlaskForm):
    option = RadioField('Trade Option', validators=[DataRequired()],
                        choices=[('Buy', 'Buy'), ('Sell', 'Sell')])
    btc_amount = FloatField('Amount (BTC)', validators=[DataRequired()])
    price = FloatField('Price')
    total = FloatField('Total')
    trade = SubmitField('Trade')


class ExplorerForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired()])
